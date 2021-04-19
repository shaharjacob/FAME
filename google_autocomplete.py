import re
import json
from pathlib import Path
from typing import List, Dict

import yaml
import click
import inflect
import requests
from click import secho
from fake_useragent import UserAgent

from dictionary import Mixed


def get_url(keyword: str, browser: str = "chrome") -> str:
    keyword.replace(" ", "+")
    return f"http://suggestqueries.google.com/complete/search?client={browser}&q={keyword}&hl=en"


def get_suggestions(keyword: str) -> List[str]:
    # headers = {"user-agent": UserAgent().chrome}
    # response = requests.get(get_url(keyword), headers=headers, verify=False)
    response = requests.get(get_url(keyword))
    suggestions = json.loads(response.text)
    return suggestions[1]


def get_query(question: str, obj1: str, obj2: str) -> str:
    # return f'"{question} {obj1} * {obj2}"'
    return f'{question} {obj1} "*" {obj2}'


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


def extend_to_plural_and_singular(engine: inflect.engine, entry: List[str], question: str, suggestions: Dict[str, str]):
    plural = engine.plural(entry[0])
    singular = engine.singular_noun(entry[0])
    if plural:
        s = get_query(question, plural, entry[1])
        suggestions[f"{plural}:{entry[1]}:{question}"] = get_suggestions(s)
    if singular:
        s = get_query(question, singular, entry[1])
        suggestions[f"{singular}:{entry[1]}:{question}"] = get_suggestions(s)
    
    plural = engine.plural(entry[1])
    singular = engine.singular_noun(entry[1])
    if plural:
        s = get_query(question, entry[0], plural)
        suggestions[f"{entry[0]}:{plural}:{question}"] = get_suggestions(s)
    if singular:
        s = get_query(question, entry[0], singular)
        suggestions[f"{entry[0]}:{singular}:{question}"] = get_suggestions(s)


def extend_synonyms(entry: List[str], question: str, suggestions: Dict[str, str]):
    mixed = Mixed(entry[0])
    synonyms = mixed.getSynonyms()
    for synonym in synonyms:
        s = get_query(question, synonym, entry[1])
        suggestions[f"{synonym}:{entry[1]}:{question}"] = get_suggestions(s)

    mixed = Mixed(entry[1])
    synonyms = mixed.getSynonyms()
    for synonym in synonyms:
        s = get_query(question, entry[0], synonym)
        suggestions[f"{entry[0]}:{synonym}:{question}"] = get_suggestions(s)


def get_elements_indecies(engine: inflect.engine, parts: List[str], suggestion: str):
    indecies = [(), (), ()]
    for i in range(3):
        res = re.search(parts[i], suggestion)
        if not res:
            plural = engine.plural(parts[i])
            if plural:
                res = re.search(plural, suggestion)
            if not res:
                singular = engine.singular_noun(parts[i])
                if singular:
                    res = re.search(singular, suggestion)
        if res:
            indecies[i] = res.span()
    return indecies


def process(d: Dict[str, List[List[str]]], plural_and_singular: bool = True, synonyms: bool = True) -> Dict[str, List[str]]:
    engine = inflect.engine()
    suggestions = {}
    for question, objects in d.items():
        for entry in objects:
            verify_question(question, entry)
            s = get_query(question, entry[0], entry[1])
            suggestions[f"{entry[0]}:{entry[1]}:{question}"] = get_suggestions(s)
            if plural_and_singular:
                extend_to_plural_and_singular(engine, entry, question, suggestions)
            if synonyms:
                extend_synonyms(entry, question, suggestions)
            
    return suggestions


def print_results(suggestions: Dict[str, List[str]]):
    already_seen = set()
    for k, v in suggestions.items():
        secho(f"{k}", fg="blue", bold=True)
        for suggestion in v:
            if suggestion in already_seen:
                continue
            already_seen.add(suggestion)
            secho(f"- {suggestion}", fg="blue")
        print() # new line


def print_results2(suggestions: Dict[str, List[str]]):
    engine = inflect.engine()
    already_seen = set()
    for k, v in suggestions.items():
        parts = k.split(':')
        for suggestion in v:
            if suggestion in already_seen:
                continue
            already_seen.add(suggestion)
            secho(f"- ", nl=False)
            indecies = get_elements_indecies(engine, parts, suggestion)
            for j, char in enumerate(suggestion):
                if indecies[0] and (indecies[0][0] <= j <= indecies[0][1]):
                    secho(f"{char}", fg="blue", nl=False)
                elif indecies[1] and (indecies[1][0] <= j <= indecies[1][1]):
                    secho(f"{char}", fg="green", nl=False)
                elif indecies[2] and (indecies[2][0] <= j <= indecies[2][1]):
                    secho(f"{char}", fg="cyan", nl=False)
                else:
                    secho(f"{char}", nl=False)
            print() # new line


def save_results(output: Path, suggestions: Dict[str, List[str]]):
    if output.suffix == '.json':
        secho(f"[INFO] Saving results json file under {str(output)}", fg="blue", bold=True)
        with open(output, 'w') as fp:
            json.dump(suggestions, fp)
    elif output.suffix == '.csv':
        secho(f"[INFO] Saving results csv file under {str(output)}", fg="blue", bold=True)
        s = ""
        for k, v in suggestions.items():
            parts = k.split(':')
            for suggestion in v:
                predicate = suggestion.replace(parts[0], "").replace(parts[1], "").replace(parts[2], "").strip()
                s += f"{parts[0]},{parts[1]},{parts[2]},{predicate}\n"
        with open(output, 'w') as fp:
            fp.write(s)
    else:
        secho(f"[WARNING] Results wasn't save under {str(output)}", fg="blue", bold=True)
        secho(f"          You should specify suffix (.json or .csv)", bold=True)




@click.command()
@click.option('-f', 'config_file', default="example.yaml", help="configuration file")
@click.option('-o', 'output', help="output file fot the results (optional)")
def main(config_file, output):
    d = read_yaml(Path(config_file))
    suggestions = process(d)
    print_results2(suggestions)
    if output:
        save_results(Path(output), suggestions)        


if __name__ == '__main__':
    main()
