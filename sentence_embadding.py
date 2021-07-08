import json
from typing import List, Tuple, Dict

import click
import inflect
import numpy as np
from click import secho
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer, util

import utils
import concept_net
import google_autosuggest
from quasimodo import Quasimodo

class SentenceEmbedding(SentenceTransformer):
    def __init__(self, model: str = 'stsb-mpnet-base-v2', init_quasimodo: bool = False, init_inflect: bool = False, save_database: bool = True, override_database: bool = False):
        super().__init__(model)
        self.embaddings = {}
        self.quasimodo = None
        if init_quasimodo:
            self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
        self.engine = None
        if init_inflect:
            self.engine = inflect.engine()
        self.override_database = override_database
        self.save_database = save_database
        self.quasimodo_edges = utils.read_json('database/quasimodo_edges.json') if save_database else {}
        self.google_edges = utils.read_json('database/google_edges.json') if save_database else {}
        self.conceptnet_edges = utils.read_json('database/conceptnet_edges.json') if save_database else {}
    
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
    
    def get_entities_relations(self, entity1: str, entity2: str) -> List[str]:
        should_save = False
        if f"{entity1}#{entity2}" in self.quasimodo_edges and not self.override_database:
            quasimodo_props = self.quasimodo_edges[f"{entity1}#{entity2}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
            quasimodo_props = self.quasimodo.get_entities_relations(entity1, entity2, n_largest=10, plural_and_singular=True)
            self.quasimodo_edges[f"{entity1}#{entity2}"] = quasimodo_props  
            should_save = True

        if f"{entity1}#{entity2}" in self.google_edges and not self.override_database:
            autocomplete_props = self.google_edges[f"{entity1}#{entity2}"]
        else:
            autocomplete_props = google_autosuggest.get_entities_relations(entity1, entity2).get("props", [])
            self.google_edges[f"{entity1}#{entity2}"] = autocomplete_props  
            should_save = True

        if f"{entity1}#{entity2}" in self.conceptnet_edges and not self.override_database:
            concept_new_props = self.conceptnet_edges[f"{entity1}#{entity2}"]
        else:
            if not self.engine:
                self.engine = inflect.engine()
            concept_new_props = concept_net.get_entities_relations(entity1, entity2, self.engine, plural_and_singular=True)
            self.conceptnet_edges[f"{entity1}#{entity2}"] = concept_new_props
            should_save = True

        if should_save:
            self.save_database_()

        return list(set(quasimodo_props + autocomplete_props + concept_new_props))
    
    def clustering(self, edge: Tuple[str], distance_threshold: float) -> Dict[int, List[str]]:
        props_edge = self.get_entities_relations(edge[0], edge[1])
        if not props_edge:
            return {}
        corpus_embeddings = self.encode(props_edge)
        corpus_embeddings = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)

        if len(props_edge) == 1:
            return {0: props_edge}
            
        clustering_model = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage='average', distance_threshold=distance_threshold)
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_

        clustered_sentences = {}
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            if cluster_id not in clustered_sentences:
                clustered_sentences[cluster_id] = []
            clustered_sentences[cluster_id].append(props_edge[sentence_id])
        return dict(sorted(clustered_sentences.items()))
    
    def save_database_(self):
        with open('database/quasimodo_edges.json', 'w') as f1:
            json.dump(self.quasimodo_edges, f1, indent='\t')
        with open('database/google_edges.json', 'w') as f2:
            json.dump(self.google_edges, f2, indent='\t')
        with open('database/conceptnet_edges.json', 'w') as f3:
            json.dump(self.conceptnet_edges, f3, indent='\t')


if __name__ == '__main__':
    model = SentenceEmbedding()
    res = model.get_entities_relations("earth", "sun")
    print(res)