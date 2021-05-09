from typing import List, Dict, Tuple

import numpy as np
from click import secho
from sentence_transformers import SentenceTransformer, util

import concept_net
from quasimodo import Quasimodo


class SentenceEmbedding(SentenceTransformer):
    def __init__(self, init_quasimodo: bool = True):
        # super().__init__('paraphrase-distilroberta-base-v1')
        super().__init__('stsb-mpnet-base-v2')
        self.embaddings = {}
        if init_quasimodo:
            self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
    
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
    
    def similarity(self, sentence1: str, sentence2: str, verbose: bool = False) -> float:
        if sentence1 not in self.embaddings:
            self.encode_sentence(sentence1)
        if sentence2 not in self.embaddings:
            self.encode_sentence(sentence2)
        similarity = util.pytorch_cos_sim(self.embaddings[sentence1]["embadding"], self.embaddings[sentence2]["embadding"])
        if verbose:
            secho(f"{sentence1} ~ {sentence2}", fg='blue')
            secho(f"Similarity: {similarity}", fg='blue', bold=True)
        return round(similarity.item(), 3)
    
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


    @staticmethod
    def print_sentence(sentence: tuple):
        secho(f"{sentence[0][0]} ", fg='red', bold=True, nl=False)
        secho(f"({sentence[0][1]}) ", fg='red', nl=False)
        secho(f"~ ", nl=False)
        secho(f"{sentence[1][0]} ", fg='green', bold=True, nl=False)
        secho(f"({sentence[1][1]}) ", fg='green', nl=False)
        secho(f"--> ", nl=False)
        secho(f"{sentence[2]}", fg='blue', bold=True)

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

    # earth = quasimodo.get_subject_props(subject='earth', n_largest=10, plural_and_singular=True)
    # earth = [f"{val[0]} {val[1]}" for val in earth]
    # electrons = quasimodo.get_subject_props(subject='electrons', n_largest=10, plural_and_singular=True)
    # electrons = [f"{val[0]} {val[1]}" for val in electrons]


    model = SentenceEmbedding()
    # model.distance(text2, text3, verbose=True)
    # model.distance(text2, text6, verbose=True)
    # model.similarity(text2, text3, verbose=True)
    # model.similarity(text2, text4, verbose=True)
    # model.similarity(text4, text5, verbose=True)
    # model.similarity(text1, text6, verbose=True)
    # model.similarity(text1, text1, verbose=True)

    # model.get_matches_between_nodes('earth', 'electrons', verbose=True)
    # model.get_matches_between_nodes('sun', 'earth', n_best=20, verbose=True)
    model.get_matches_between_edges(('sun', 'earth'), ('nucleus', 'electrons'), n_best=20, verbose=True)
    print()
    print()
    model.get_matches_between_edges(('earth', 'sun'), ('electrons', 'nucleus'), n_best=20, verbose=True)
    # res = quasimodo.get_subject_object_props('earth', 'sun', n_largest=10, plural_and_singular=True)
    # aa = util.paraphrase_mining(model, res)
    # for a in aa:
    #     print(f"{a[0]}, {res[a[1]]}, {res[a[2]]}")
    # arr = []
    # for e in earth:
    #     for electron in electrons:
    #         arr.append((e, electron, model.similarity(e, electron)))

    # sort_arr = sorted(arr, key=lambda x: -x[2])
    # for a in sort_arr:
    #     print(a)