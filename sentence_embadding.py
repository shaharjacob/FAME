from typing import List, Dict

import numpy as np
from click import secho
from sentence_transformers import SentenceTransformer, util

class SentenceEmbedding(SentenceTransformer):
    def __init__(self):
        # super().__init__('paraphrase-distilroberta-base-v1')
        super().__init__('stsb-mpnet-base-v2')
        self.embaddings = {}
    
    def encode_sentences(self, sentences: List[str]):
        embeddings = super().encode(sentences)
        for sentence, embedding in zip(sentences, embeddings):
            self.embaddings[sentence] = {
                "sentence": sentence,
                "norm": np.linalg.norm(embedding),
                "embadding": embedding,
            }
    
    def encode_sentence(self, sentence: str):
        embedding = super().encode(sentence)
        self.embaddings[sentence] = {
            "sentence": sentence,
            "norm": np.linalg.norm(embedding),
            "embadding": embedding,
        }

    def distance(self, sentence1: str, sentence2: str, verbose: bool = False) -> float:
        if sentence1 not in self.embaddings:
            self.encode_sentence(sentence1)
        if sentence2 not in self.embaddings:
            self.encode_sentence(sentence2)
        distance = np.linalg.norm(self.embaddings[sentence1]["embadding"] - self.embaddings[sentence2]["embadding"])
        if verbose:
            secho(f"{sentence1} ~ {sentence2}", fg='blue')
            secho(f"Distance: {distance}", fg='blue', bold=True)
        return distance
    
    def similarity(self, sentence1: str, sentence2: str, verbose: bool = False) -> float:
        if sentence1 not in self.embaddings:
            self.encode_sentence(sentence1)
        if sentence2 not in self.embaddings:
            self.encode_sentence(sentence2)
        similarity = util.pytorch_cos_sim(self.embaddings[sentence1]["embadding"], self.embaddings[sentence2]["embadding"])
        if verbose:
            secho(f"{sentence1} ~ {sentence2}", fg='blue')
            secho(f"Similarity: {similarity}", fg='blue', bold=True)
        return similarity


if __name__ == "__main__":
    text1 = 'earth orbit sun'
    text2 = 'earth revolve around sun'
    text3 = 'earth spin around sun'
    text4 = 'earth circle the sun'
    text5 = 'earth smaller than the sun'
    text6 = 'dog is the best friend of human'
    text7 = "This is a red cat with a hat."
    text8 = "Have you seen my red cat?"
    sentences = [text1, text2, text3, text4, text5, text6]

    from quasimodo import Quasimodo
    quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
    earth = quasimodo.get_subject_props(subject='earth', n_largest=10, plural_and_singular=True)
    earth = [f"{val[0]} {val[1]}" for val in earth]
    electrons = quasimodo.get_subject_props(subject='electrons', n_largest=10, plural_and_singular=True)
    electrons = [f"{val[0]} {val[1]}" for val in electrons]


    model = SentenceEmbedding()
    # model.distance(text2, text3, verbose=True)
    # model.distance(text2, text6, verbose=True)
    # model.similarity(text2, text3, verbose=True)
    # model.similarity(text2, text4, verbose=True)
    # model.similarity(text4, text5, verbose=True)
    # model.similarity(text1, text6, verbose=True)
    # model.similarity(text1, text1, verbose=True)

    arr = []
    for e in earth:
        for electron in electrons:
            arr.append((e, electron, model.similarity(e, electron)))

    sort_arr = sorted(arr, key=lambda x: -x[2])
    for a in sort_arr:
        print(a)