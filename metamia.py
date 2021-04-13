import re
import csv
from pathlib import Path
from typing import List, Dict

import click
import requests
import pandas as pd
from click import secho
from bs4 import BeautifulSoup


def beautify_text(text: str, prefix: str, remove: str) -> str:
    # removing prefix (a, b or what) and removing html tags
    text = re.sub("<[/A-Za-z]*>", "", text)
    text = re.sub(remove, "", text)
    return text[len(prefix):-1] if text[-1] == ' ' else text[len(prefix):]


# def extract_from_text(text: str, prefix: str, end: str):
#     matches = re.findall(f'{prefix}.+?(?={end})', text)
#     return [beautify_text(match, prefix) for match in matches]


def extract_subject(soup: BeautifulSoup, class_name: str, prefix: str, remove: str = "") -> List[str]:
    all_instances = soup.find_all("span", attrs={"class": class_name})
    return [beautify_text(instance.string, prefix, remove) for instance in all_instances]

def extract_explaination(soup: BeautifulSoup) -> List[str]:
    all_instances = soup.find_all("div", attrs={"class": "concept_1_wrapper"})
    return [beautify_text(instance.text, "What:  ", "") for instance in all_instances]


def read_page() -> str:
    try:
        response = requests.get('http://www.metamia.com/randomly-sample-the-analogy-database')
        return response.text
    except:
        return ""


@click.command()
@click.option('-i', '--iterations', default=5, help="How many iterations to do")
@click.option('-o', '--output', default="out2.csv", help="Path for the output file")
def run(iterations: int, output: str):
    entries = []
    for i in range(iterations):
        secho(f"parsing page {i} out of {iterations}", fg='blue', bold=True)
        text = read_page()
        if not text:
            continue
        soup = BeautifulSoup(text, 'html.parser')
        a = extract_subject(soup, "analogyA_wrapper", "a:  ", "~")
        b = extract_subject(soup, "analogyB_wrapper", "b:  ")
        what = extract_explaination(soup)

        for j in range(len(a)):
            entries.append({
                "a": a[j],
                "b": b[j],
                "reason": what[j],
            })

    with open(output, "w", newline='') as f:
        dict_writer = csv.DictWriter(f, entries[0].keys())
        dict_writer.writeheader()
        for entry in entries:
            try:
                dict_writer.writerow(entry)
            except:
                secho(f"[ERROR] can't write {entry['a']} ~ {entry['b']}")

    if Path(output).exists():
        df = pd.read_csv(output)
        df = df.drop_duplicates(subset=list(df.columns))
        df.to_csv(output, index=False)


if __name__ == "__main__":
    run()

    