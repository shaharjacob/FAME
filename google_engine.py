import json
from pathlib import Path

import yaml
import click
import requests
from click import secho
from fake_useragent import UserAgent


def get_url(keyword: str, browser: str = "chrome"):
    keyword.replace(" ", "+")
    return f"http://suggestqueries.google.com/complete/search?output={browser}&q={keyword}"


def get_suggestions(keyword: str):
    headers = {"user-agent": UserAgent().chrome}
    response = requests.get(get_url(keyword), headers=headers, verify=False)
    suggestions = json.loads(response.text)
    return suggestions[1]


def get_query(question: str, obj1: str, obj2: str):
    return f'{question} {obj1} "*" {obj2}'


def read_yaml(path: Path):
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


def verify_question(question: str, objects: dict):
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


def process(d: dict):
    suggestions = {}
    for question, objects in d.items():
        for entry in objects:
            verify_question(question, entry)
            s = get_query(question, entry[0], entry[1])
            suggestions[f"{entry[0]}:{entry[1]}:{question}"] = get_suggestions(s)
    return suggestions


def print_results(suggestions: dict):
    for k, v in suggestions.items():
        secho(f"{k}", fg="blue", bold=True)
        for suggestion in v:
            secho(f"- {suggestion}", fg="blue")
        print() # new line


def save_results(output: Path, suggestions: dict):
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
    print_results(suggestions)
    if output:
        save_results(Path(output), suggestions)        


if __name__ == '__main__':
    main()