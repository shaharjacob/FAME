import json
from pathlib import Path
from itertools import combinations
from typing import List, Tuple, Dict

import click
import inflect
import numpy as np
from click import secho
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer, util

import testset
import concept_net
# import networkx as nx
import google_autocomplete
from wikifier import Wikifier
# import matplotlib.pyplot as plt
from quasimodo import Quasimodo

# avilable models can be found here: https://huggingface.co/models?sort=downloads&search=sentence-transformers&p=0
# paraphrase-xlm-r-multilingual-v1
# stsb-mpnet-base-v2
# stsb-roberta-large


class SentenceEmbedding(SentenceTransformer):
    def __init__(self, model: str = 'stsb-mpnet-base-v2', init_quasimodo: bool = True, init_inflect: bool = True, save_database=True):
        super().__init__(model)
        self.embaddings = {}
        if init_quasimodo:
            self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
        if init_inflect:
            self.engine = inflect.engine()
        self.save_database = save_database
        self.quasimodo_edges = read_json('database/quasimodo_edges.json') if save_database else {}
        self.google_edges = read_json('database/google_edges.json') if save_database else {}
        self.conceptnet_edges = read_json('database/conceptnet_edges.json') if save_database else {}
    
    def encode_sentences(self, sentences: List[str]):
        embeddings = super().encode(sentences)
        for sentence, embedding in zip(sentences, embeddings):
            self.embaddings[sentence] = embedding
    
    def encode_sentence(self, sentence: str):
        embedding = super().encode(sentence)
        self.embaddings[sentence] = embedding
    
    def similarity(self, sentence1: str, sentence2: str, verbose: bool = False) -> float:
        if sentence1 not in self.embaddings:
            self.encode_sentence(sentence1)
        if sentence2 not in self.embaddings:
            self.encode_sentence(sentence2)

        similarity = round(util.pytorch_cos_sim(self.embaddings[sentence1], self.embaddings[sentence2]).item(), 3)
        if verbose:
            secho(f"{sentence1} ~ {sentence2}", fg='blue')
            secho(f'Similarity: {similarity}', fg='blue', bold=True)
        return similarity
    
    def get_nodes_score(self, node1: str, node2: str, n_best: int = 0, verbose: bool = False) -> List[Tuple]:
        if not self.quasimodo:
            self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
        props_node1 = SentenceEmbedding.get_node_props(node1, self.quasimodo)
        props_node2 = SentenceEmbedding.get_node_props(node2, self.quasimodo)

        sentences = []
        for prop1 in props_node1:
            for prop2 in props_node2:
                sentences.append(((prop1, node1), (prop2, node2), self.similarity(prop1, prop2)))
        sentences = sorted(sentences, key=lambda x: -x[2])
        if n_best > 0:
            sentences = sentences[:n_best]
        if verbose:
            for sentence in sentences:
                SentenceEmbedding.print_sentence(sentence)
        return sentences
    
    def get_edge_props(self, head: str, tail: str) -> List[str]:
        if f"{head}#{tail}" in self.quasimodo_edges:
            quasimodo_props = self.quasimodo_edges[f"{head}#{tail}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
            quasimodo_props = self.quasimodo.get_edge_props(head, tail, n_largest=10, plural_and_singular=True)
            self.quasimodo_edges[f"{head}#{tail}"] = quasimodo_props  

        if f"{head}#{tail}" in self.google_edges:
            autocomplete_props = self.google_edges[f"{head}#{tail}"]
        else:
            autocomplete_props = google_autocomplete.get_edge_props(head, tail).get((head, tail), {"suggestions": [], "props": []}).get("props", [])
            self.google_edges[f"{head}#{tail}"] = autocomplete_props  

        if f"{head}#{tail}" in self.conceptnet_edges:
            concept_new_props = self.conceptnet_edges[f"{head}#{tail}"]
        else:
            if not self.engine:
                self.engine = inflect.engine()
            concept_new_props = concept_net.get_edge_props(self.engine, head, tail)
            self.conceptnet_edges[f"{head}#{tail}"] = concept_new_props                
        return list(set(quasimodo_props + autocomplete_props + concept_new_props))

    def get_edges_score(self, edge1: Tuple[str], edge2: Tuple[str], n_best: int = 0, verbose: bool = False):
        props_edge1 = self.get_edge_props(edge1[0], edge1[1])
        props_edge2 = self.get_edge_props(edge2[0], edge2[1])

        sentences = []
        for prop1 in props_edge1:
            for prop2 in props_edge2:
                sentences.append(((prop1, f"{edge1[0]} -> {edge1[1]}"), (prop2, f"{edge2[0]} -> {edge2[1]}"), self.similarity(prop1, prop2)))
        sentences = sorted(sentences, key=lambda x: -x[2])
        if n_best > 0:
            sentences = sentences[:n_best]
        if verbose:
            for sentence in sentences:
                SentenceEmbedding.print_sentence(sentence)
        
        score = 0
        if sentences:
            score = round(sum([val[2] for val in sentences]) / len(sentences), 3)

        return {
            "sentences": sentences,
            "score": score,
        }
    
    def clustering(self, edge: Tuple[str], distance_threshold: float) -> Dict[int, List[str]]:
        props_edge = self.get_edge_props(edge[0], edge[1])
        corpus_embeddings = self.encode(props_edge)
        corpus_embeddings = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)

        clustering_model = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage='average', distance_threshold=distance_threshold)
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_

        clustered_sentences = {}
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            if cluster_id not in clustered_sentences:
                clustered_sentences[cluster_id] = []
            clustered_sentences[cluster_id].append(props_edge[sentence_id])
        return clustered_sentences
    
    def save_datebase(self):
        with open('database/quasimodo_edges.json', 'w') as f1:
            json.dump(self.quasimodo_edges, f1)
        with open('database/google_edges.json', 'w') as f2:
            json.dump(self.google_edges, f2)
        with open('database/conceptnet_edges.json', 'w') as f3:
            json.dump(self.conceptnet_edges, f3)

    @staticmethod
    def print_sentence(sentence: tuple, show_nouns: bool = True):
        secho(f"{sentence[0][0]} ", fg='red', bold=show_nouns, nl=False)
        if show_nouns:
            secho(f"({sentence[0][1]}) ", fg='red', nl=False)
        secho(f"~ ", nl=False)
        secho(f"{sentence[1][0]} ", fg='green', bold=show_nouns, nl=False)
        if show_nouns:
            secho(f"({sentence[1][1]}) ", fg='green', nl=False)
        secho(f"--> ", nl=False)
        secho(f"{sentence[2]}", fg='blue', bold=show_nouns)

    @staticmethod
    def get_node_props(node: str, quasimodo: Quasimodo):
        props = []
        quasimodo_props = quasimodo.get_node_props(node=node, n_largest=10, plural_and_singular=True)
        quasimodo_props = [f"{val[0]} {val[1]}" for val in quasimodo_props]
        props.extend(quasimodo_props)
        props.extend(concept_net.hasProperty(engine=quasimodo.engine, subject=node, n=10, weight_thresh=1, plural_and_singular=True))
        props.extend(concept_net.capableOf(engine=quasimodo.engine, subject=node, n=10, weight_thresh=1, plural_and_singular=True))
        props.extend(concept_net.isA(engine=quasimodo.engine, subject=node, n=10, weight_thresh=1, plural_and_singular=True))
        props.extend(concept_net.usedFor(engine=quasimodo.engine, subject=node, n=10, weight_thresh=1, plural_and_singular=True))
        return props
    
    @staticmethod
    def get_all_combs(nouns: List[str]) -> List[List[Tuple[str]]]:
        return [
            [(nouns[0], nouns[1]), (nouns[2], nouns[3])],
            [(nouns[0], nouns[1]), (nouns[3], nouns[2])],
            [(nouns[1], nouns[0]), (nouns[2], nouns[3])],
            [(nouns[1], nouns[0]), (nouns[3], nouns[2])],
            [(nouns[0], nouns[2]), (nouns[1], nouns[3])],
            [(nouns[0], nouns[2]), (nouns[3], nouns[1])],
            [(nouns[2], nouns[0]), (nouns[1], nouns[3])],
            [(nouns[2], nouns[0]), (nouns[3], nouns[1])],
            [(nouns[0], nouns[3]), (nouns[1], nouns[2])],
            [(nouns[0], nouns[3]), (nouns[2], nouns[1])],
            [(nouns[3], nouns[0]), (nouns[1], nouns[2])],
            [(nouns[3], nouns[0]), (nouns[2], nouns[1])],
        ]


def read_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def run(sentence1: str, 
        sentence2: str, 
        verbose: bool = False, 
        full_details: bool = False, 
        model: str = "stsb-mpnet-base-v2", 
        addition_nouns=[]) -> dict:

    secho(f"- {sentence1}", fg="blue")
    secho(f"- {sentence2}", fg="blue")

    # TODO
    addition_nouns = [noun for noun in addition_nouns if noun in sentence1.split()]

    # part of speech
    w = Wikifier(sentence1)
    nouns1 = w.get_specific_part_of_speech("nouns", normForm=False)
    Wikifier.remove_parts_of_compound_nouns(nouns1)
    nouns1 = sorted(list(set(nouns1 + addition_nouns)))

    w = Wikifier(sentence2)
    nouns2 = w.get_specific_part_of_speech("nouns", normForm=False)
    Wikifier.remove_parts_of_compound_nouns(nouns2)
    nouns2 = sorted(list(set(nouns2)))

    secho(f"\nNouns: ", fg="blue", bold=True)
    secho(f"- {nouns1}", fg="blue")
    secho(f"- {nouns2}\n", fg="blue")

    combs1 = list(combinations(nouns1, 2))
    reverse_combs1 = [(comb[1], comb[0]) for comb in combs1]
    combs1 += reverse_combs1

    combs2 = list(combinations(nouns2, 2))
    reverse_combs2 = [(comb[1], comb[0]) for comb in combs2]
    combs2 += reverse_combs2

    secho(f"[INFO] create SentenceEmbedding object", fg="blue")
    model = SentenceEmbedding(model=model)

    matches = []
    # secho(f"[INFO] Total combinations to process: ", fg="blue", nl=False)
    # secho(f"{len(combs1) * len(combs2)}", fg="blue", bold=True)
    for i, comb1 in enumerate(combs1):
        for j, comb2 in enumerate(combs2):
            # secho(f"{(i * len(combs2)) + j + 1}", fg="blue", bold=True, nl=False)
            # secho(f" out of ", fg="blue", nl=False)
            # secho(f"{len(combs1) * len(combs2)}", fg="blue", bold=True)
            # model.bipartite_edges(comb1, comb2)
            res = model.get_edges_score(comb1, comb2, n_best=10)
            matches.append(((comb1, comb2), res["score"], res["sentences"]))
    
    if model.save_database:
        model.save_datebase()

    matches = sorted(matches, key=lambda x: -x[1])
    if verbose:
        for match in matches:
            secho(f"({match[0][0][0]} --> {match[0][0][1]})", fg='red', bold=True, underline=True, nl=False)
            secho(f", ", underline=True, nl=False)
            secho(f"({match[0][1][0]} --> {match[0][1][1]}) ", fg='green', bold=True, underline=True, nl=False)
            secho(f"--avg--> ", underline=True, nl=False)
            secho(f"{match[1]}", fg='blue', bold=True, underline=True)
            if full_details:
                for m in match[2]:
                    SentenceEmbedding.print_sentence(m, show_nouns=False)
                print()
    
    return {
        "score": matches[0][1],
        "match": matches[0][0],
    }


def validation():
    score = 0
    for i, sample in enumerate(test.testset):
        res = main(sample["input"][0], sample["input"][1], verbose=True, full_details=True, model='stsb-mpnet-base-v2', addition_nouns=['sunscreen'])
        if res["score"] == 0:
            secho(f"Wrong answer for sample number {i}", fg="red", bold=True)
            secho(f"  no connection found...\n", fg="red")
            continue
        if res["edges"] == sample["label"] or res["edges"] == (sample["label"][1], sample["label"][0]):
            score += 1
        else:
            secho(f"Wrong answer for sample number {i}", fg="red", bold=True)
            secho(f"  Expected: {sample['label']}", fg="red")
            secho(f"  Actual: {res['edges']}\n", fg="red")
    secho(f"\nSuccess {score}/{len(test.testset)}", fg="green", bold=True)    


def main(sentence1: str, 
         sentence2: str, 
         verbose: bool = True, 
         full_details: bool = False, 
         threshold: float = 0.5, 
         model: str = "stsb-mpnet-base-v2", 
         addition_nouns: str = []) -> dict:
    res = run(sentence1, sentence2, verbose, full_details, model, addition_nouns)
    secho(f"\n--------------------------------------------------")
    secho(f"Match: ", fg="blue", nl=False)
    secho(f"{res['match'][0][0]} --> {res['match'][0][1]}  ~  {res['match'][1][0]} --> {res['match'][1][1]}", fg="blue", bold=True)
    secho(f"Score: ", fg="blue", nl=False)
    secho(f"{res['score']}", fg="blue", bold=True)
    secho(f"Is analogy: ", fg="blue", nl=False)
    secho(f"{res['score'] > threshold}", fg="blue", bold=True)
    secho(f"--------------------------------------------------\n")
    return {
        "edges": res["match"],
        "score": res["score"],
        "is_analogy": res["score"] > threshold,
    }


@click.command()
@click.option('-s1', '--sentence1', default="The nucleus, which is positively charged, and the electrons which are negatively charged, compose the atom", 
                help="First sentence")
@click.option('-s2', '--sentence2', default="On earth, the atmosphere protects us from the sun, but not enough so we use sunscreen", 
                help="Second sentence")
@click.option('--verbose', is_flag=True,
                help="Print all the edges and their scores")
@click.option('--full-details', is_flag=True,
                help="Print all the scores inside the edges (which lead to the edge score)")
@click.option('--threshold', default=0.5,
                help="Threshold to determine if this is analogy or not")
@click.option('-a', '--addition-nouns', default=[], multiple=True, 
                help="Addition nouns in case of Wikifier is failed to recognize (sunscreen)")
def cli(sentence1: str, sentence2: str, verbose: bool, full_details: bool, threshold: float, addition_nouns: str) -> bool:
    res = main(sentence1, sentence2, verbose, full_details, threshold, addition_nouns=addition_nouns)
    return res


if __name__ == "__main__":
    # cli()

    # main(sentences[0], sentences[1], verbose=True, full_details=True, model='stsb-mpnet-base-v2', addition_nouns=['sunscreen'])

    validation()
