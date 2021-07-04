import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

import yaml
import click
import inflect
import requests
from tqdm import tqdm
from click import secho


class GoogleAutoSuggestOneEntity(object):
    def __init__(self,
                question: str,
                entity: str,
                prop: str,
                browser: str = 'chrome',
                pattern1: str = '%s %s %s .*',
                pattern2: str = '%s .* %s %s',
                regex1: str = '%s %s %s (.*)',
                regex2: str = '%s (.*) %s %s'):
        self.entity = entity
        self.prop = prop
        self.browser = browser
        self.keywords = [pattern1 % (question, entity, prop), pattern2 % (question, prop, entity)]
        self.regexs = [regex1 % (question, prop, entity), regex2 % (question, prop, entity)] 
        self.suggestinos = self.init_suggestions()

    def init_suggestions(self) -> List[Tuple[str]]:
        sugges: List[Tuple[str]] = []
        for keyword_, regex_ in zip(self.keywords, self.regexs):
            keyword = keyword_.replace(" ", "+")
            url = f"http://suggestqueries.google.com/complete/search?client={self.browser}&q={keyword}&hl=us"
            response = requests.get(url)
            suggestions = json.loads(response.text)[1]
            for suggestion in suggestions:
                match = re.match(regex_, suggestion)
                if match:
                    sugges.append(match.group(1))
        return list(set(sugges))


class GoogleAutoSuggestTwoEntities(object):
    def __init__(self, 
                question: str, 
                node1: str, 
                node2: str, 
                browser: str = 'chrome',
                pattern: str = '%s %s .* %s', 
                regex: str = '^%s( a)?( an)?( the)? %s (.*) %s$'):
        self.question = question
        self.node1 = node1
        self.node2 = node2
        self.browser = browser
        self.keyword = pattern % (question, node1, node2)
        self.regex = regex % (question, node1, node2)
        self.suggestions: List[Tuple[str]] = self.init_suggestions()

    def init_suggestions(self) -> List[Tuple[str]]:
        sugges: List[Tuple[str]] = []
        keyword = self.keyword.replace(" ", "+")
        url = f"http://suggestqueries.google.com/complete/search?client={self.browser}&q={keyword}&hl=us"
        response = requests.get(url)
        suggestions = json.loads(response.text)[1]
        for suggestion in suggestions:
            match = re.match(self.regex, suggestion)
            if match:
                parts = suggestion.split()
                pairs = [f"{parts[i]} {parts[i+1]}" for i in range(len(parts) - 1)]
                if all(elem in (parts + pairs) for elem in [self.node1, self.node2, self.question]):
                    sugges.append((suggestion, match.group(4)))
        return list(set(sugges))

    def render_single_suggestion(self, suggestion: tuple):
        res = re.search(self.question, suggestion[0])
        if not res: return
        question_indecies = res.span()

        res = re.search(self.node1, suggestion[0])
        if not res: return
        node1_indecies = res.span()

        res = re.search(self.node2, suggestion[0])
        if not res: return
        node2_indecies = res.span()

        secho(f"- ", nl=False)
        for j, char in enumerate(suggestion[0]):
            if (question_indecies[0] <= j <= question_indecies[1]):
                secho(f"{char}", fg="blue", nl=False)
            elif (node1_indecies[0] <= j <= node1_indecies[1]):
                secho(f"{char}", fg="green", nl=False)
            elif (node2_indecies[0] <= j <= node2_indecies[1]):
                secho(f"{char}", fg="cyan", nl=False)
            else:
                secho(f"{char}", nl=False)

        spaces = ''.join([' '] * max((50 - len(suggestion[0])), 1))
        secho(f"{spaces}--> ({self.keyword})")

    def render(self):
        for suggestion in self.suggestions:
            self.render_single_suggestion(suggestion)


def extend_to_plural_and_singular(engine: inflect.engine, entry: List[str], question: str, suggestions: List[Tuple[str]], verbose: bool = True):
    plural = engine.plural(entry[0])
    singular = engine.singular_noun(entry[0])

    if plural:
        googleAC = GoogleAutoSuggestTwoEntities(question, plural, entry[1])
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions["suggestions"]:
                if verbose:
                    googleAC.render_single_suggestion(suggestion)
                suggestions["suggestions"].append(suggestion[0])
                suggestions["props"].append(suggestion[1])
    if singular:
        googleAC = GoogleAutoSuggestTwoEntities(question, singular, entry[1])
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions["suggestions"]:
                if verbose:
                    googleAC.render_single_suggestion(suggestion)
                suggestions["suggestions"].append(suggestion[0])
                suggestions["props"].append(suggestion[1])
    
    plural = engine.plural(entry[1])
    singular = engine.singular_noun(entry[1])

    if plural:
        googleAC = GoogleAutoSuggestTwoEntities(question, entry[0], plural)
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions["suggestions"]:
                if verbose:
                    googleAC.render_single_suggestion(suggestion)
                suggestions["suggestions"].append(suggestion[0])
                suggestions["props"].append(suggestion[1])
    if singular:
        googleAC = GoogleAutoSuggestTwoEntities(question, entry[0], singular)
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions["suggestions"]:
                if verbose:
                    googleAC.render_single_suggestion(suggestion)
                suggestions["suggestions"].append(suggestion[0])
                suggestions["props"].append(suggestion[1])


def get_entity_suggestions(entity: str, prop: str):
    suggestions = []
    for question in ["why does", "why do", "why did", "how does", "how do", "how did"]:
        model = GoogleAutoSuggestOneEntity(question, entity, prop)
        suggestions.extend(model.suggestinos)
    return list(set(suggestions))


def get_edge_props(node1: str, node2: str) -> List[str]:
    d = {
        "why do": [[node1, node2]],
        "why does": [[node1, node2]],
        "why did": [[node1, node2]],
        "how do": [[node1, node2]],
        "how does": [[node1, node2]],
        "how did": [[node1, node2]],
    }
    return process(d, verbose=False)


def process(d: Dict[str, List[List[str]]], plural_and_singular: bool = True, verbose: bool = True) -> List[str]:
    engine = inflect.engine()
    suggestions = {}
    for question, objects in d.items():
        if verbose:
            secho(f"\n[INFO] collect information on question '{question}'", fg="blue")
        iterator = tqdm(objects) if verbose else objects
        for entry in iterator:
            if (entry[0], entry[1]) not in suggestions:
                suggestions[(entry[0], entry[1])] = {
                    "suggestions": [],
                    "props": [],
                }
            googleAC = GoogleAutoSuggestTwoEntities(question, entry[0], entry[1])
            for suggestion in googleAC.suggestions:
                if suggestion[0] not in suggestions[(entry[0], entry[1])]["suggestions"]:
                    if verbose:
                        googleAC.render_single_suggestion(suggestion)
                    suggestions[(entry[0], entry[1])]["suggestions"].append(suggestion[0])
                    suggestions[(entry[0], entry[1])]["props"].append(suggestion[1])
            if plural_and_singular:
                extend_to_plural_and_singular(engine, entry, question, suggestions[(entry[0], entry[1])], verbose=verbose)

    return suggestions


if __name__ == '__main__':
    for q in ["why does", "why do", "why did", "how does", "how do", "how did"]:
        model = GoogleAutoSuggestOneEntity(q, "electricity", "discovered")
        print(model.suggestinos)