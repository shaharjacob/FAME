from typing import List, Dict

from click import secho
from PyDictionary import PyDictionary


class Dictionary(PyDictionary):
    def __init__(self, *args):
        super().__init__(*args)
    
    def getMeanings(self, verbose: bool = True) -> Dict[str, Dict[str, List[str]]]:
        meanings = super().getMeanings()
        if verbose:
            for word, parts_of_speech in meanings.items():
                secho(f"{word}", fg="blue", bold=True)
                if parts_of_speech:
                    for part_of_speech, explainations in parts_of_speech.items():
                        secho(f"  - {part_of_speech.lower()}:", fg="blue", bold=True)
                        for explaination in explainations:
                            secho(f"    - {explaination}", fg="blue")
                        secho("")
                else:
                    secho(f"  - No meaning found - skipping...", fg="blue")
        return meanings
    
    def getAntonyms(self, n: int = 0, verbose: bool = True) -> List[Dict[str, List[str]]]:
        all_antonyms = super().getAntonyms()
        catoff = len(all_antonyms)
        if n > 0 and n <= len(all_antonyms):
            catoff = n
        all_antonyms = all_antonyms[:catoff]
        if verbose:
            for antonyms in all_antonyms:
                for word, antonyms_words in antonyms.items():
                    secho(f"{word}", fg="blue", bold=True)
                    secho(f"  - ", fg="blue", nl=False)
                    for antonym in antonyms_words:
                        secho(f"{antonym}, ", fg="blue", nl=False)
                    secho("")
                secho("")
        return all_antonyms
    
    def getSynonyms(self, n: int = 0, verbose: bool = True) -> List[Dict[str, List[str]]]:
        all_synonyms = super().getSynonyms()
        catoff = len(all_synonyms)
        if n > 0 and n <= len(all_synonyms):
            catoff = n
        all_synonyms = all_synonyms[:catoff]
        if verbose:
            for synonyms in all_synonyms:
                for word, synonyms_words in synonyms.items():
                    secho(f"{word}", fg="blue", bold=True)
                    secho(f"  - ", fg="blue", nl=False)
                    for synonym in synonyms_words:
                        secho(f"{synonym}, ", fg="blue", nl=False)
                    secho("")
                secho("")
        return all_synonyms


class WordNet():
    def __init__(self, word: str):
        self.word = word
        from nltk.corpus import wordnet
        self.synsets = wordnet.synsets(word)

    def getAntonyms(self, verbose: bool = True) -> List[str]:
        antonyms = set()
        for syn in self.synsets:
            for lm in syn.lemmas():
                if lm.antonyms():
                    antonyms.add(lm.antonyms()[0].name())
        if verbose:
            secho(f"Antonyms: ", fg="blue", bold=True, nl=False)
            if len(antonyms) > 0:
                for antonym in antonyms:
                    secho(f"{antonym}, ", fg="blue", nl=False)
            else:
                secho(f"No match found for '{self.word}'", fg="blue", nl=False)
            secho("\n")

        return list(antonyms)
    
    def getSynonyms(self, verbose: bool = True) -> List[str]:
        synonyms = set()
        for syn in self.synsets:
            for lm in syn.lemmas():
                synonyms.add(lm.name())
        
        if verbose:
            secho(f"Synonyms: ", fg="blue", bold=True, nl=False)
            if len(synonyms) > 0:
                for synonym in synonyms:
                    secho(f"{synonym}, ", fg="blue", nl=False)
            else:
                secho(f"No match found for '{self.word}'", fg="blue", nl=False)
            secho("\n")

        return list(synonyms)
    
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


if __name__ == "__main__":


    word = WordNet('horse')
    word.getDefinitions()
    word.getExamples()
    word.getAntonyms()
    word.getSynonyms()


    # dictionary = Dictionary("horse")
    # dictionary.getMeanings()
    # dictionary.getAntonyms()
    # dictionary.getSynonyms()
