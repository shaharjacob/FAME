import re
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Tuple

import inflect
import requests
from click import secho

root = Path(__file__).resolve().parent.parent.parent

IGNORE = ["a"]

def read_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

class GoogleAutoSuggestEntityProps(object):
    def __init__(self,
                entity: str,
                prop: str,
                regex: str = '%s %s (.*)',
                browser: str = 'chrome'):
        self.entity = entity
        self.prop = prop
        self.browser = browser
        self.regex = regex % (entity, prop)
        self.suggestinos = self.init_suggestions()
    
    def init_suggestions(self) -> List[Tuple[str]]:
        sugges: List[str] = []
        keyword = f"{self.entity} {self.prop}".replace(" ", "+")
        url = f"http://suggestqueries.google.com/complete/search?client={self.browser}&q={keyword}&hl=en"
        time.sleep(2)
        response = requests.get(url)
        if response.status_code == 403:
            secho(f"[WARNING] cannot access to {url}", fg="yellow", bold=True)
            os.environ['SKIP_GOOGLE'] = 'true'
            return []
        
        suggestions = json.loads(response.text)[1]
        for suggestion in suggestions:
            match = re.match(self.regex, suggestion)
            if match:
                sugges.append(match.group(1))
        return list(set(sugges))



class GoogleAutoSuggestOneEntity(object):
    def __init__(self,
                question: str,
                entity: str,
                prop: str,
                browser: str = 'chrome',
                pattern1: str = '%s %s %s',
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
        sugges: List[str] = []
        for keyword_, regex_ in zip(self.keywords, self.regexs):
            keyword = keyword_.replace(" ", "+")
            url = f"http://suggestqueries.google.com/complete/search?client={self.browser}&q={keyword}&hl=en"
            time.sleep(2)
            response = requests.get(url)
            if response.status_code == 403:
                secho(f"[WARNING] cannot access to {url}", fg="yellow", bold=True)
                os.environ['SKIP_GOOGLE'] = 'true'
                return []
        
            suggestions = json.loads(response.text)[1]
            for suggestion in suggestions:
                match = re.match(regex_, suggestion)
                if match:
                    sugges.append(match.group(1))
        return list(set(sugges))


class GoogleAutoSuggestTwoEntities(object):
    def __init__(self, 
                question: str, 
                entity1: str, 
                entity2: str, 
                browser: str = 'chrome',
                pattern: str = '%s %s .* %s', 
                regex: str = '^%s( a)?( an)?( the)? %s (.*) %s$'):
        self.question = question
        self.entity1 = entity1
        self.entity2 = entity2
        self.browser = browser
        self.keyword = pattern % (question, entity1, entity2)
        self.regex = regex % (question, entity1, entity2)
        self.suggestions: List[Tuple[str]] = self.init_suggestions()

    def init_suggestions(self) -> List[Tuple[str]]:
        already_seen = set()
        sugges: List[Tuple[str]] = []
        keyword = self.keyword.replace(" ", "+")
        curser = len(self.question) + len(self.entity1) + 2
        language = 'en'
        url = f"http://suggestqueries.google.com/complete/search?client={self.browser}&q={keyword}&hl={language}&cp={curser}"
        time.sleep(2)
        response = requests.get(url)
        if response.status_code == 403:
            secho(f"[WARNING] cannot access to {url}", fg="yellow", bold=True)
            os.environ['SKIP_GOOGLE'] = 'true'
            return []
        
        suggestions = json.loads(response.text)[1]
        for suggestion in suggestions:
            match = re.match(self.regex, suggestion)
            if match:
                parts = suggestion.split()
                # we looking for entity1, entity2 and the question inside the suggestion.
                # because they can be two words, we need to allow it also. otherwise they will not be found.
                pairs = [f"{parts[i]} {parts[i+1]}" for i in range(len(parts) - 1)]
                # it also can be three words, for example 'why does it'
                threes = [f"{parts[i]} {parts[i+1]} {parts[i+2]}" for i in range(len(parts) - 2)]
                if all(elem in (parts + pairs + threes) for elem in [self.entity1, self.entity2, self.question]):
                    prop = match.group(4)
                    if prop not in already_seen not in IGNORE:
                        sugges.append((suggestion, prop))
                        already_seen.add(prop)
        return sugges

    def render_single_suggestion(self, suggestion: tuple):
        # looking the indecies of the question
        res = re.search(self.question, suggestion[0])
        if not res: return
        question_indecies = res.span()

        # looking the indecies of the first entity
        res = re.search(self.entity1, suggestion[0])
        if not res: return
        entity1_indecies = res.span()

        # looking the indecies of the second entity
        res = re.search(self.entity2, suggestion[0])
        if not res: return
        entity2_indecies = res.span()

        # the thing here is to print with different colors depend of the indecies that we found above
        secho(f"- ", nl=False)
        for j, char in enumerate(suggestion[0]):
            if (question_indecies[0] <= j <= question_indecies[1]):
                secho(f"{char}", fg="blue", nl=False)
            elif (entity1_indecies[0] <= j <= entity1_indecies[1]):
                secho(f"{char}", fg="green", nl=False)
            elif (entity2_indecies[0] <= j <= entity2_indecies[1]):
                secho(f"{char}", fg="cyan", nl=False)
            else:
                secho(f"{char}", nl=False)

        spaces = ''.join([' '] * max((50 - len(suggestion[0])), 1))
        secho(f"{spaces}--> ({self.keyword})")


def extend_suggestions(entity1: str, entity2: str, question: str, suggestions: List[Tuple[str]], verbose: bool):
    googleAC = GoogleAutoSuggestTwoEntities(question, entity1, entity2)
    if 'SKIP_GOOGLE' in os.environ:
        return
    for suggestion in googleAC.suggestions:
        if suggestion[0] not in suggestions["suggestions"] and suggestion[1] not in suggestions["props"]:
            if verbose:
                googleAC.render_single_suggestion(suggestion)
            suggestions["suggestions"].append(suggestion[0])
            suggestions["props"].append(suggestion[1])


def extend_to_plural_and_singular(engine: inflect.engine, entity1: str, entity2: str, question: str, suggestions: List[Tuple[str]], verbose: bool = False):
    # extend the first entity
    plural = engine.plural(entity1)
    if plural:
        extend_suggestions(plural, entity2, question, suggestions, verbose)

    singular = engine.singular_noun(entity1)
    if singular:
        extend_suggestions(singular, entity2, question, suggestions, verbose)

    # extend the second entity
    plural = engine.plural(entity2)
    if plural:
        extend_suggestions(entity1, plural, question, suggestions, verbose)

    singular = engine.singular_noun(entity2)
    if singular:
        extend_suggestions(entity1, singular, question, suggestions, verbose)


def get_entity_suggestions(entity: str, prop: str, plural_and_singular: bool = False):
    # given an entity and prop, it will suggest new entities to complete the sentence.
    # for example, given entity 'electricity' and prop 'discovered', it will return entities like: faraday, edison, benjamin
    if plural_and_singular: 
        engine = inflect.engine()
    suggestions = []
    for question in ["why do", "why is", "why does", "why does it",  "why did", "how do", "how is", "how does", "how does it", "how did"]:
        # time.sleep(1) # google policy
        model = GoogleAutoSuggestOneEntity(question, entity, prop)
        if 'SKIP_GOOGLE' in os.environ:
            return list(set(suggestions))
        suggestions.extend(model.suggestinos)
        if plural_and_singular:
            plural = engine.plural(entity)
            if plural and plural != entity:
                model = GoogleAutoSuggestOneEntity(question, plural, prop)
                if 'SKIP_GOOGLE' in os.environ:
                    return list(set(suggestions))
                suggestions.extend(model.suggestinos)

            singular = engine.singular_noun(entity)
            if singular and singular != plural and singular != entity:
                model = GoogleAutoSuggestOneEntity(question, singular, prop)
                if 'SKIP_GOOGLE' in os.environ:
                    return list(set(suggestions))
                suggestions.extend(model.suggestinos)

    return list(set(suggestions))


# def get_entity_props(entity: str):
#     # given an entity, it will give some props that charactrize this entity.
#     # for example, given entity 'newton', it will return props like: derived unit, fundamental unit, measure of
#     google_db = read_json(root / 'backend' / 'database' / 'google_nodes.json')
#     if entity not in google_db:
#         suggestions = []
#         for p in ["is a", "is a type of"]:
#             model = GoogleAutoSuggestEntityProps(entity, p)
#             suggestions.extend(model.suggestinos)
#         google_db[entity] = sorted(list(set(suggestions)))
#         with open(root / 'backend' / 'database' / 'google_nodes.json', 'w') as f:
#             json.dump(google_db, f, indent='\t')
#     return google_db[entity]


def get_entities_relations(entity1: str, entity2: str, plural_and_singular: bool = True, verbose: bool = False) -> Dict[str, List[str]]:
    # given two entities, it will give the relations between them.
    # The order is important! get_entities_relations(entity1, entity2) != get_entities_relations(entity2, entity1)
    # for example, if entity1=earth, entity2=sun, it will return relations like: revolve around, not fall into, orbit.
    d = {
        "why do": [entity1, entity2],
        "why is": [entity1, entity2],
        "why does": [entity1, entity2],
        "why does it": [entity1, entity2],
        "why did": [entity1, entity2],
        "how do": [entity1, entity2],
        "how is": [entity1, entity2],
        "how does": [entity1, entity2],
        "how does it": [entity1, entity2],
        "how did": [entity1, entity2],
    }
    return process(d, plural_and_singular=plural_and_singular, verbose=verbose)


def process(d: Dict[str, List[List[str]]], plural_and_singular: bool = True, verbose: bool = False) -> Dict[str, List[str]]:
    engine = inflect.engine()
    suggestions = {"suggestions": [], "props": []}
    for question, objects in d.items():
        if verbose:
            secho(f"\n[INFO] collect information on question '{question}'", fg="blue")
        entity1, entity2 = objects
        googleAC = GoogleAutoSuggestTwoEntities(question, entity1, entity2)
        if 'SKIP_GOOGLE' in os.environ:
            return suggestions
        for suggestion in googleAC.suggestions:
            if suggestion[0] not in suggestions["suggestions"] and suggestion[1] not in suggestions["props"]:
                if verbose:
                    googleAC.render_single_suggestion(suggestion)
                # we want the whole suggestion and not only the prop for better visualization and debugging
                suggestions["suggestions"].append(suggestion[0])
                suggestions["props"].append(suggestion[1])
        if plural_and_singular:
            extend_to_plural_and_singular(engine, entity1, entity2, question, suggestions, verbose=verbose)
    return suggestions


if __name__ == '__main__':
    # res = get_entity_suggestions("electricity", "discovered")
    # res = get_entity_props("sun")
    # res = get_entities_relations("electricity", "cell", verbose=True).get("props")
    res = get_entities_relations("sun", "earth", verbose=True).get("props")
    print(res)