from typing import List, Dict

from click import secho
from PyDictionary import PyDictionary

import gensim.downloader as api
# word_vectors = api.load("glove-twitter-25")
word_vectors = api.load("glove-wiki-gigaword-100")

from nltk_import import download_package
download_package('wordnet', 'corpora')
from nltk.corpus import wordnet

class WordNet():
    def __init__(self, word: str):
        self.word = word
        self.synsets = wordnet.synsets(word)

    def getAntonyms(self, verbose: bool = True, n: int = 0) -> List[str]:
        antonyms = set()
        for syn in self.synsets:
            for lm in syn.lemmas():
                if lm.antonyms():
                    antonyms.add(lm.antonyms()[0].name())
        
        antonyms = list(antonyms)
        if (n > 0) and (len(antonyms) > 0) and (n <= len(antonyms)):
            new_antonyms = []
            for antonym in antonyms:
                try:
                    word_vectors.get_vector(antonym)
                    new_antonyms.append(antonym)
                except:
                    secho(f"[WARNING] word ({antonym}) not appear in the vocabulary", fg="yellow")
            new_antonyms = sorted(new_antonyms, key=lambda s: word_vectors.distance(s, self.word))
            antonyms = new_antonyms[:n]

        if verbose:
            secho(f"[WordNet][Antonyms]({self.word}): ", fg="blue", bold=True, nl=False)
            if len(antonyms) > 0:
                for antonym in antonyms:
                    secho(f"{antonym}, ", fg="cyan", nl=False)
            else:
                secho(f"No match found for '{self.word}'", fg="blue", nl=False)
            secho("\n")

        return list(antonyms)
    
    def getSynonyms(self, verbose: bool = True, n: int = 0) -> List[str]:
        synonyms = set()
        for syn in self.synsets:
            for lm in syn.lemmas():
                synonyms.add(lm.name())
        
        synonyms = list(synonyms)
        if (n > 0) and (len(synonyms) > 0) and (n <= len(synonyms)):
            new_synonyms = []
            for synonym in synonyms:
                try:
                    word_vectors.get_vector(synonym)
                    new_synonyms.append(synonym)
                except:
                    secho(f"[WARNING] word ({synonym}) not appear in the vocabulary", fg="yellow")
            new_synonyms = sorted(new_synonyms, key=lambda s: word_vectors.distance(s, self.word))
            synonyms = new_synonyms[:n]
        
        if verbose:
            secho(f"[WordNet][Synonyms]({self.word}): ", fg="blue", bold=True, nl=False)
            if len(synonyms) > 0:
                for synonym in synonyms:
                    secho(f"{synonym}, ", fg="cyan", nl=False)
            else:
                secho(f"No match found for '{self.word}'", fg="blue", nl=False)
            secho("\n")

        return synonyms
    
    def getDefinitions(self, verbose: bool = True) -> List[List[str]]:
        definitions = [[str(syn)[8:-2].split('.')[0], syn.definition()] for syn in self.synsets]
        if verbose:
            secho(f"Definitions:", fg="blue", bold=True)
            if len(definitions) > 0:
                for definition in definitions:
                    secho(f"  - {definition[0]}: ", fg="blue", bold=True, nl=False)
                    secho(f"{definition[1]}, ", fg="blue")
            else:
                secho(f"No match found for '{self.word}'", fg="blue")
            secho("\n")

        return definitions

    def getExamples(self, verbose: bool = True) -> List[List[str]]:
        examples = [[str(syn)[8:-2].split('.')[0], syn.examples()] for syn in self.synsets]
        if verbose:
            secho(f"Examples:", fg="blue", bold=True)
            if len(examples) > 0:
                for example in examples:
                    secho(f"  - {example[0]}: ", fg="blue", bold=True, nl=False)
                    if example[1]:
                        for ex in example[1]:
                            secho(f"{ex}, ", fg="blue", nl=False)
                        secho("")
                    else:
                        secho(f"no example found", fg="blue")
            else:
                secho(f"No match found for '{self.word}'", fg="blue")
            secho("\n")
        
        return examples


class Dictionary(PyDictionary):
    def __init__(self, *args):
        super().__init__(*args)
    
    def getMeanings(self, verbose: bool = True) -> Dict[str, Dict[str, List[str]]]:
        meanings = super().getMeanings()
        if verbose:
            secho(f"Meaning:", fg="blue", bold=True)
            for word, parts_of_speech in meanings.items():
                secho(f"  - {word}", fg="blue", bold=True)
                if parts_of_speech:
                    for part_of_speech, explainations in parts_of_speech.items():
                        secho(f"    - {part_of_speech.lower()}:", fg="blue", bold=True)
                        for explaination in explainations:
                            secho(f"      - {explaination}", fg="blue")
                        secho("")
                else:
                    secho(f"    - No meaning found - skipping...", fg="blue")
        return meanings
    
    def getAntonyms(self, verbose: bool = True, n: int = 0,) -> List[Dict[str, List[str]]]:
        all_antonyms = super().getAntonyms()
        all_antonyms = [antonym for antonym in all_antonyms if antonym]
        for i, antonyms in enumerate(all_antonyms):
            for word, antonyms_words in antonyms.items():
                if (n > 0) and (len(antonyms_words) > 0) and (n <= len(antonyms_words)):
                    new_antonyms_words = []
                    for antonyms_word in antonyms_words:
                        try:
                            word_vectors.get_vector(antonyms_word)
                            new_antonyms_words.append(antonyms_word)
                        except:
                            secho(f"[WARNING] word ({antonyms_word}) not appear in the vocabulary", fg="yellow")
                    new_antonyms_words = sorted(new_antonyms_words, key=lambda s: word_vectors.distance(s, word))
                    all_antonyms[i][word] = new_antonyms_words[:n]

        if verbose:
            for antonyms in all_antonyms:
                for word, antonyms_words in antonyms.items():
                    secho(f"[Dictionary][Antonyms]({word}): ", fg="blue", bold=True, nl=False)
                    for antonym in antonyms_words:
                        secho(f"{antonym}, ", fg="cyan", nl=False)
                    secho("")
                secho("")
        return all_antonyms
    
    def getSynonyms(self, verbose: bool = True, n: int = 0) -> List[Dict[str, List[str]]]:
        all_synonyms = super().getSynonyms()
        all_synonyms = [synonym for synonym in all_synonyms if synonym]
        for i, synonyms in enumerate(all_synonyms):
            if not synonyms:
                continue
            for word, synonyms_words in synonyms.items():
                if (n > 0) and (len(synonyms_words) > 0) and (n <= len(synonyms_words)):
                    new_synonyms_words = []
                    for synonyms_word in synonyms_words:
                        try:
                            word_vectors.get_vector(synonyms_word)
                            new_synonyms_words.append(synonyms_word)
                        except:
                            secho(f"[WARNING] word ({synonyms_word}) not appear in the vocabulary", fg="yellow")
                    new_synonyms_words = sorted(new_synonyms_words, key=lambda s: word_vectors.distance(s, word))
                    all_synonyms[i][word] = new_synonyms_words[:n]

        if verbose:
            for synonyms in all_synonyms:
                for word, synonyms_words in synonyms.items():
                    secho(f"[Dictionary][Synonyms]({word}): ", fg="blue", bold=True, nl=False)
                    for synonym in synonyms_words:
                        secho(f"{synonym}, ", fg="cyan", nl=False)
                    secho("")
                secho("")
        return all_synonyms


class Mixed:
    def __init__(self, word: str):
        self.word = word
        self.wordnet = WordNet(word)
        self.dictionary = Dictionary(word)
    
    def getSynonyms(self, verbose: bool = True, n: int = 5):
        wordnet_synonyms = self.wordnet.getSynonyms(verbose, n)
        dictionary_synonyms = self.dictionary.getSynonyms(verbose, n)
        if dictionary_synonyms:
            if self.word in dictionary_synonyms[0]:
                dictionary_synonyms = dictionary_synonyms[0][self.word]
            else:
                dictionary_synonyms = []
        
        synonyms = wordnet_synonyms + dictionary_synonyms
        new_synonyms = set()
        for synonym in synonyms:
            try:
                word_vectors.get_vector(synonym)
                new_synonyms.add(synonym)
            except:
                secho(f"[WARNING] word ({synonym}) not appear in the vocabulary", fg="yellow")

        new_synonyms = list(new_synonyms)
        new_synonyms = sorted(new_synonyms, key=lambda s: word_vectors.distance(s, self.word))
        synonyms = new_synonyms[:n]
        secho(f"Best {n} synonyms for {self.word}", fg="blue", bold=True)
        secho(f" - ", fg="green", nl=False)
        for synonym in synonyms:
            secho(f"{synonym}, ", fg="green", nl=False)
        print('\n')
        return synonyms
    
    def getAntonyms(self, verbose: bool = True, n: int = 5):
        wordnet_antonyms = self.wordnet.getAntonyms(verbose, n)
        dictionary_antonyms = self.dictionary.getAntonyms(verbose, n)
        if dictionary_antonyms:
            if self.word in dictionary_antonyms[0]:
                dictionary_antonyms = dictionary_antonyms[0][self.word]
            else:
                dictionary_antonyms = []
        
        antonyms = wordnet_antonyms + dictionary_antonyms
        new_antonyms = set()
        for antonym in antonyms:
            try:
                word_vectors.get_vector(antonym)
                new_antonyms.add(antonym)
            except:
                secho(f"[WARNING] word ({antonym}) not appear in the vocabulary", fg="yellow")

        new_antonyms = list(new_antonyms)
        new_antonyms = sorted(new_antonyms, key=lambda s: word_vectors.distance(s, self.word))
        antonyms = new_antonyms[:n]
        secho(f"Best {n} antonyms for {self.word}", fg="blue", bold=True)
        secho(f" - ", fg="blue", nl=False)
        for antonym in antonyms:
            secho(f"{antonym}, ", fg="blue", nl=False)
        print('\n')
        return antonyms




if __name__ == "__main__":

    # word = WordNet('horse')
    # print(word.getDefinitions())
    # print(word.getExamples())
    # print(word.getAntonyms())
    # print(word.getSynonyms(n=5))


    # dictionary = Dictionary("horse")
    # dictionary.getMeanings()
    # print(dictionary.getAntonyms())
    # print(dictionary.getSynonyms(n=5))

    mixed = Mixed('increase')
    mixed.getSynonyms()
    # pass