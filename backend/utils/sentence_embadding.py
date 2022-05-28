from typing import List, Dict

import torch
import numpy as np
from click import secho
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer, util

device = "cuda" if torch.cuda.is_available() else "cpu"
# device = "mps" if torch.backends.mps.is_available() else device


class SentenceEmbedding(SentenceTransformer):
    def __init__(self, model: str = 'msmarco-distilbert-base-v4'):
        super().__init__(model, device=device)
        self.embaddings = {}

    
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
    

    def clustering(self, tokens: List[str], distance_threshold: float) -> Dict[int, List[str]]:
        if not tokens:
            return {}
        
        # only one token. No calculation is needed
        if len(tokens) == 1:
            return {0: tokens}
        
        # https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/clustering/agglomerative.py
        corpus_embeddings = self.encode(tokens)
        corpus_embeddings = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)

        # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
        clustering_model = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage='average', distance_threshold=distance_threshold)
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_

        clustered_sentences = {}
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            if cluster_id not in clustered_sentences:
                clustered_sentences[cluster_id] = []
            clustered_sentences[cluster_id].append(tokens[sentence_id])

        # the key is the id of the cluster (0,1,...) and the value is a list of props
        return dict(sorted(clustered_sentences.items()))
    


if __name__ == '__main__':
    pass