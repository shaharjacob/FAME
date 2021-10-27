import os
from pathlib import Path
from typing import List, Tuple, Dict

import numpy as np
from click import secho
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer, util

from mapping.data_collector import DataCollector

backend_dir = Path(__file__).resolve().parent.parent
if 'SENTENCE_TRANSFORMERS_HOME' not in os.environ:
    if not (backend_dir / 'cache').exists():
        (backend_dir / 'cache').mkdir()
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(backend_dir / 'cache')

class SentenceEmbedding(SentenceTransformer):
    def __init__(self, model: str = 'msmarco-distilbert-base-v4', data_collector: DataCollector = None):
        super().__init__(model)
        self.embaddings = {}
        self.data_collector = data_collector

    
    def encode_sentence(self, sentence: str):
        # saving the embadding of the given sentence
        embedding = super().encode(sentence)
        self.embaddings[sentence] = embedding
    

    def similarity(self, sentence1: str, sentence2: str, verbose: bool = False) -> float:
        # first we will get the embadding of the two given sentences
        if sentence1 not in self.embaddings:
            self.encode_sentence(sentence1)
        if sentence2 not in self.embaddings:
            self.encode_sentence(sentence2)

        # https://www.sbert.net/docs/usage/semantic_textual_similarity.html
        similarity = round(util.pytorch_cos_sim(self.embaddings[sentence1], self.embaddings[sentence2]).item(), 3)
        if verbose:
            secho(f"{sentence1} ~ {sentence2},  ", fg='blue', nl=False)
            secho(f'Similarity: {similarity}', fg='blue', bold=True)
        return similarity
    

    def clustering(self, edge: Tuple[str], distance_threshold: float) -> Dict[int, List[str]]:
        # clustering properties of an given edge
        if not self.data_collector:
            self.data_collector = DataCollector()
        props_edge = self.data_collector.get_entities_relations(edge[0], edge[1])
        if not props_edge:
            return {}
        
        # https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/clustering/agglomerative.py
        corpus_embeddings = self.encode(props_edge)
        corpus_embeddings = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)

        # only one property is found
        if len(props_edge) == 1:
            return {0: props_edge}
        
        # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
        clustering_model = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage='average', distance_threshold=distance_threshold)
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_

        clustered_sentences = {}
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            if cluster_id not in clustered_sentences:
                clustered_sentences[cluster_id] = []
            clustered_sentences[cluster_id].append(props_edge[sentence_id])

        # the key is the id of the cluster (0,1,...) and the value is a list of props
        return dict(sorted(clustered_sentences.items()))
    


if __name__ == '__main__':
    pass