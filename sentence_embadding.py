from itertools import combinations
from typing import List, Tuple

import click
from click import secho
from sentence_transformers import SentenceTransformer, util

import concept_net
from wikifier import Wikifier
from quasimodo import Quasimodo


class SentenceEmbedding(SentenceTransformer):
    def __init__(self, model: str = 'stsb-mpnet-base-v2', init_quasimodo: bool = True):
        # avilable models can be found here: https://huggingface.co/models?sort=downloads&search=sentence-transformers&p=0
        # paraphrase-xlm-r-multilingual-v1
        # stsb-mpnet-base-v2
        # stsb-roberta-large
        super().__init__(model)
        self.embaddings = {}
        if init_quasimodo:
            self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
    
    def encode_sentences(self, sentences: List[str]):
        embeddings = super().encode(sentences)
        for sentence, embedding in zip(sentences, embeddings):
            self.embaddings[sentence] = {
                "sentence": sentence,
                "embadding": embedding,
            }
    
    def encode_sentence(self, sentence: str):
        embedding = super().encode(sentence)
        self.embaddings[sentence] = {
            "sentence": sentence,
            "embadding": embedding,
        }
    
    def similarity(self, sentence1: str, sentence2: str, verbose: bool = False) -> float:
        if sentence1 not in self.embaddings:
            self.encode_sentence(sentence1)
        if sentence2 not in self.embaddings:
            self.encode_sentence(sentence2)
        similarity = util.pytorch_cos_sim(self.embaddings[sentence1]["embadding"], self.embaddings[sentence2]["embadding"])
        similarity = round(similarity.item(), 3)
        if verbose:
            secho(f"{sentence1} ~ {sentence2}", fg='blue')
            secho(f"Similarity: {similarity}", fg='blue', bold=True)
        return similarity
    
    def get_matches_between_nodes(self, noun1: str, noun2: str, n_best: int = 0, verbose: bool = False) -> List[Tuple]:
        props_noun1 = SentenceEmbedding.get_noun_props(noun1, self.quasimodo)
        props_noun2 = SentenceEmbedding.get_noun_props(noun2, self.quasimodo)

        sentences = []
        for prop1 in props_noun1:
            for prop2 in props_noun2:
                sentences.append(((prop1, noun1), (prop2, noun2), self.similarity(prop1, prop2)))
        sentences = sorted(sentences, key=lambda x: -x[2])
        if n_best > 0:
            sentences = sentences[:n_best]
        if verbose:
            for sentence in sentences:
                SentenceEmbedding.print_sentence(sentence)
        return sentences
    
    def get_matches_between_edges(self, pair1: Tuple[str], pair2: Tuple[str], n_best: int = 0, verbose: bool = False):
        props_pair1 = self.quasimodo.get_subject_object_props(pair1[0], pair1[1], n_largest=10, plural_and_singular=True)
        props_pair2 = self.quasimodo.get_subject_object_props(pair2[0], pair2[1], n_largest=10, plural_and_singular=True)
        
        sentences = []
        for prop1 in props_pair1:
            for prop2 in props_pair2:
                sentences.append(((prop1, f"{pair1[0]} -> {pair1[1]}"), (prop2, f"{pair2[0]} -> {pair2[1]}"), self.similarity(prop1, prop2)))
        sentences = sorted(sentences, key=lambda x: -x[2])
        if n_best > 0:
            sentences = sentences[:n_best]
        if verbose:
            for sentence in sentences:
                SentenceEmbedding.print_sentence(sentence)
        return sentences
    
    def match_paris(self, nouns: List[str], verbose: bool = False):
        if len(nouns) != 4:
            secho(f"[ERROR] you should give excatly 4 nouns ({len(nouns)} was given)", fg='red', bold=True)
            exit(1)

        matches = []
        combs = SentenceEmbedding.get_all_combs(nouns)
        for comb in combs:
            res = self.get_matches_between_edges(comb[0], comb[1], n_best=5)
            score = 0
            if res:
                score = sum([val[2] for val in res]) / len(res)
            matches.append((comb, score))

        matches = sorted(matches, key=lambda x: -x[1])
        if verbose:
            for match in matches:
                secho(f"({match[0][0][0]} --> {match[0][0][1]})", fg='red', bold=True, nl=False)
                secho(f", ", nl=False)
                secho(f"({match[0][1][0]} --> {match[0][1][1]}) ", fg='green', bold=True, nl=False)
                secho(f"----> ", nl=False)
                secho(f"{match[1]}", fg='blue', bold=True)
        
        return {
            "score": matches[0][1],
            "match": matches[0][0],
        }
                
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
    def get_noun_props(noun: str, quasimodo: Quasimodo):
        props = []
        quasimodo_props = quasimodo.get_subject_props(subject=noun, n_largest=10, plural_and_singular=True)
        quasimodo_props = [f"{val[0]} {val[1]}" for val in quasimodo_props]
        props.extend(quasimodo_props)
        props.extend(concept_net.hasProperty(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True))
        props.extend(concept_net.capableOf(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True))
        props.extend(concept_net.isA(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True))
        props.extend(concept_net.usedFor(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True))
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
    for comb1 in combs1:
        for comb2 in combs2:
            res = model.get_matches_between_edges(comb1, comb2, n_best=5)
            score = 0
            if res:
                score = round(sum([val[2] for val in res]) / len(res), 3)
            matches.append(((comb1, comb2), score, res))
    
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


def main(sentence1: str, 
         sentence2: str, 
         verbose: bool = True, 
         full_details: bool = False, 
         threshold: float = 0.5, 
         model: str = "stsb-mpnet-base-v2", 
         addition_nouns: str = []) -> bool:
    res = run(sentence1, sentence2, verbose, full_details, model, addition_nouns)
    secho(f"\n--------------------------------------------------")
    secho(f"Match: ", fg="blue", nl=False)
    secho(f"{res['match'][0][0]} --> {res['match'][0][1]}  ~  {res['match'][1][0]} --> {res['match'][1][1]}", fg="blue", bold=True)
    secho(f"Score: ", fg="blue", nl=False)
    secho(f"{res['score']}", fg="blue", bold=True)
    secho(f"Is analogy: ", fg="blue", nl=False)
    secho(f"{res['score'] > threshold}", fg="blue", bold=True)
    secho(f"--------------------------------------------------\n")
    return res["score"] > threshold


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
    # main()

    # text1 = 'earth revolve around the sun'
    # text2 = 'earth circle the sun'
    # text3 = 'dog is the best friend of human'

    # model = SentenceEmbedding()
    # model.similarity(text1, text3, verbose=True)

    sentence1 = "On earth, the atmosphere protects us from the sun, but not enough so we use sunscreen"
    sentence2 = "The nucleus, which is positively charged, and the electrons which are negatively charged, compose the atom"

    sentence3= "A singer expresses what he thinks by songs"
    sentence4 = "A programmer expresses what he thinks by writing code"

    main(sentence3, sentence4, verbose=True, full_details=True, model='stsb-mpnet-base-v2', addition_nouns=['sunscreen'])

