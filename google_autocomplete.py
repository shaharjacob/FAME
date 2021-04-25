import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

import yaml
import click
import inflect
import requests
from click import secho

from dictionary import Mixed

class GoogleAutocomplete(object):
    def __init__(self, 
                question: str, 
                obj1: str, 
                obj2: str, 
                browser: str = 'chrome',
                pattern: str = '%s %s "*" %s', 
                regex: str = '^%s.* %s .* %s.*$'):
        self.question = question
        self.obj1 = obj1
        self.obj2 = obj2
        self.browser = browser
        self.keyword = pattern % (question, obj1, obj2)
        self.regex = regex % (question, obj1, obj2)
        self.suggestions: List[Tuple[str]] = self.init_suggestions()

    def init_suggestions(self) -> List[Tuple[str]]:
        sugges: List[Tuple[str]] = []
        keyword = self.keyword.replace(" ", "+")
        url = f"http://suggestqueries.google.com/complete/search?client={self.browser}&q={keyword}&hl=en"
        response = requests.get(url)
        suggestions = json.loads(response.text)[1]
        for suggestion in suggestions:
            if re.match(self.regex, suggestion):
                sugges.append((suggestion, self.keyword))
        return list(set(sugges))

    def render_single_suggestion(self, suggestion: tuple):
        res = re.search(self.question, suggestion[0])
        if not res: return
        question_indecies = res.span()

        res = re.search(self.obj1, suggestion[0])
        if not res: return
        obj1_indecies = res.span()

        res = re.search(self.obj2, suggestion[0])
        if not res: return
        obj2_indecies = res.span()

        secho(f"- ", nl=False)
        for j, char in enumerate(suggestion[0]):
            if (question_indecies[0] <= j <= question_indecies[1]):
                secho(f"{char}", fg="blue", nl=False)
            elif (obj1_indecies[0] <= j <= obj1_indecies[1]):
                secho(f"{char}", fg="green", nl=False)
            elif (obj2_indecies[0] <= j <= obj2_indecies[1]):
                secho(f"{char}", fg="cyan", nl=False)
            else:
                secho(f"{char}", nl=False)

        spaces = ''.join([' '] * max((40 - len(suggestion[0])), 1))
        secho(f"{spaces}--> ({suggestion[1]})")

    def render(self):
        for suggestion in self.suggestions:
            self.render_single_suggestion(suggestion)


def verify_question(question: str, objects: List[str]):
    valid_questions = [
        'why do',
        'how do',
    ]
    if question not in valid_questions:
        secho(f"[ERROR] yaml file is not valid", fg="red", bold=True)
        secho(f"        The question {question} should be one of the following: {valid_questions}", fg="red")
        exit(1)
    if len(objects) != 2:
        secho(f"[ERROR] yaml file is not valid", fg="red", bold=True)
        secho(f"        Two objects (str) should be defined in every entry", fg="red")
        exit(1)


def read_yaml(path: Path) -> Dict[str, List[List[str]]]:
    if not path.exists():
        secho(f"[ERROR] file {path} is not exists!", fg="red", bold=True)
        exit(1)
    with open(path, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            secho(f"[ERROR] while loading yaml file {path}", fg="red", bold=True)
            secho(f"        {exc}", fg="red")
            exit(1)


def extend_to_plural_and_singular(engine: inflect.engine, entry: List[str], question: str, suggestions: List[Tuple[str]]):
    plural = engine.plural(entry[0])
    singular = engine.singular_noun(entry[0])

    if plural:
        googleAC = GoogleAutocomplete(question, plural, entry[1])
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions:
                googleAC.render_single_suggestion(suggestion)
                suggestions.append(suggestion[0])
    if singular:
        googleAC = GoogleAutocomplete(question, singular, entry[1])
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions:
                googleAC.render_single_suggestion(suggestion)
                suggestions.append(suggestion[0])
    
    plural = engine.plural(entry[1])
    singular = engine.singular_noun(entry[1])

    if plural:
        googleAC = GoogleAutocomplete(question, entry[0], plural)
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions:
                googleAC.render_single_suggestion(suggestion)
                suggestions.append(suggestion[0])
    if singular:
        googleAC = GoogleAutocomplete(question, entry[0], singular)
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions:
                googleAC.render_single_suggestion(suggestion)
                suggestions.append(suggestion[0])


def extend_synonyms(entry: List[str], question: str, suggestions: Dict[str, str]):
    mixed = Mixed(entry[0])
    synonyms = mixed.getSynonyms(verbose=False)
    for synonym in synonyms:
        googleAC = GoogleAutocomplete(question, synonym, entry[1])
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions:
                googleAC.render_single_suggestion(suggestion)
                suggestions.append(suggestion[0])

    mixed = Mixed(entry[1])
    synonyms = mixed.getSynonyms(verbose=False)
    for synonym in synonyms:
        googleAC = GoogleAutocomplete(question, entry[0], synonym)
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions:
                googleAC.render_single_suggestion(suggestion)
                suggestions.append(suggestion[0])


def process(d: Dict[str, List[List[str]]], plural_and_singular: bool = True, synonyms: bool = True) -> List[str]:
    engine = inflect.engine()
    suggestions = []
    for question, objects in d.items():
        for entry in objects:
            verify_question(question, entry)
            googleAC = GoogleAutocomplete(question, entry[0], entry[1])
            for suggestion in googleAC.suggestions:
                if suggestion[0] not in suggestions:
                    googleAC.render_single_suggestion(suggestion)
                    suggestions.append(suggestion[0])
            if plural_and_singular:
                extend_to_plural_and_singular(engine, entry, question, suggestions)
            if synonyms:
                extend_synonyms(entry, question, suggestions)

    return list(set(suggestions))


@click.command()
@click.option('-f', 'config_file', default="example.yaml", help="configuration file")
def main(config_file):
    d = read_yaml(Path(config_file))
    suggestions = process(d)


if __name__ == '__main__':
    main()
