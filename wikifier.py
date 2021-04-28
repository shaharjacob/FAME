import re
import json
from typing import List, Dict

import requests
from click import secho

BASE_URL = 'http://www.wikifier.org/annotate-article'
KEY = 'vuxrrjzclzvyzdrtsnlggedddjwagc'
LANG = 'en'
BG_COLORS = {
    'verbs': 'green',
    'nouns': 'red',
    'adverbs': 'yellow',
    'adjectives': 'cyan',
    'NA': '',
}
FG_COLORS = {
    'verbs': 'black',
    'nouns': 'black',
    'adverbs': 'black',
    'adjectives': 'black',
    'NA': '',
}


class Wikifier:
    def __init__(self, text: str):
        self.text = self.init_text(text)
        self.data = self.init_data()
        self.words = self.init_words()
        self.part_of_speech = self.init_part_of_speech()


    def init_text(self, text: str) -> str:
        s = re.sub('[^A-Za-z0-9 ,]+', '', text)
        if s != text:
            secho(f"[WARNING] Special character where found, proccesing the following text:", fg="yellow", bold=True)
            secho(f"          {s}", fg="yellow")
        return re.sub(r"\s+", ' ', s)


    def init_data(self) -> Dict:
        url = f'{BASE_URL}?userKey={KEY}&text={self.text}&lang={LANG}&partsOfSpeech=true'
        try:
            response = requests.get(url)
        except:
            secho(f"[ERROR] Failed to get information from {url}", fg="red", bold=True)
            exit(1)
        return json.loads(response.text)


    def init_words(self) -> List[Dict]:
        words = []
        current_word = []
        for i, char in enumerate(self.text):
            if i == len(self.text) - 1:  # last character
                if char != ' ' and char != ',':
                    current_word.append(char)
                words.append({
                    "start": i - len(current_word) + 1,
                    "end": i + 1,
                    "value": ''.join(current_word),
                    "type": 'NA',
                })
            
            elif char == ' ':  # new word
                words.append({
                    "start": i - len(current_word),
                    "end": i,
                    "value": ''.join(current_word),
                    "type": 'NA',
                })
                current_word = []
            
            elif char == ',':
                words.append({
                    "start": i - len(current_word),
                    "end": i,
                    "value": ''.join(current_word),
                    "type": 'NA',
                })
                current_word = [',']

            else:
                current_word.append(char)
        return words



    def init_part_of_speech(self) -> List[Dict]:
        types = ['verbs', 'nouns', 'adjectives', 'adverbs']
        part_of_speech = []
        for t in types:
            for v in self.data.get(t, []):
                part_of_speech.append({
                    'start': v['iFrom'], 
                    'end': v['iTo'] + 1, 
                    'value': v['normForm'],
                    'type': t,
                })
        return sorted(part_of_speech, key=lambda x: x['start'])


    def get_part_of_speech(self, verbose: bool = True) -> List[Dict]:
        for part in self.part_of_speech:
            # if part["value"] == self.text[part["start"]:part["end"]]:
            for i, word in enumerate(self.words):
                if part["start"] == word["start"] and part["end"] == word["end"]:
                    self.words[i].update({
                        'type': part['type'],
                    })
                    break

        if verbose:
            for i, word in enumerate(self.words):
                secho(f"{word['value']}", fg=FG_COLORS[word['type']], bg=BG_COLORS[word['type']], nl=False)
                if i < len(self.words) - 1:
                    if self.words[i + 1]["value"] != ',':
                        secho(f" ", nl=False)
            secho("")
            secho("")
            Wikifier.print_color_key()
        return self.words


    def get_specific_part_of_speech(self, which: str, normForm: bool = True) -> List[str]:
        if normForm:
            return [v['normForm'] for v in self.data.get(which, [])]
        else:
            return [self.text[v['iFrom']:v['iTo'] + 1] for v in self.data.get(which, [])]
    

    @staticmethod
    def remove_parts_of_compound_nouns(nouns: List[str]):
        to_remove = set()
        for noun in nouns:
            parts = noun.split()
            if len(parts) > 1:
                for noun_ in nouns:
                    if noun_ == parts[0] or noun_ == parts[1]:
                        to_remove.add(noun_)
        for noun_to_remove in to_remove:
            nouns.remove(noun_to_remove)
        return nouns

    @staticmethod
    def print_color_key():
        secho("Color key: ", nl=False)
        secho("verbs", fg=FG_COLORS['verbs'], bg=BG_COLORS['verbs'], nl=False)
        secho(", ", nl=False)
        secho("nouns", fg=FG_COLORS['nouns'], bg=BG_COLORS['nouns'], nl=False)
        secho(", ", nl=False)
        secho("adjectives", fg=FG_COLORS['adjectives'], bg=BG_COLORS['adjectives'], nl=False)
        secho(", ", nl=False)
        secho("adverbs", fg=FG_COLORS['adverbs'], bg=BG_COLORS['adverbs'], nl=False)


    def save(self, path: str = 'wikifier.json'):
        with open(path, 'w') as f:
            json.dump(self.data, f)
        

if __name__ == "__main__":
    # text = "I love coding but sometimes coding is very boring"
    # text = "sunscreen protects against the sun as a tarpaulin protects against rain"
    # text = 'sunscreen protects against the sun'
    text = 'why do horses kick stable doors'
    w = Wikifier(text)
    w.get_part_of_speech()


