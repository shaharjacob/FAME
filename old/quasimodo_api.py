import os
import math
from pathlib import Path
from typing import List, Dict, Tuple, Set

import inflect
import requests
import pandas as pd
from tqdm import tqdm
from click import secho
from pandas import DataFrame
from bs4 import BeautifulSoup


def read_page(filter_by: Dict[str, str], page: int = 1) -> str:
    try:
        keywords = []
        for k, v in filter_by.items():
            keywords.extend([k.replace(' ', '+'), '=', v.replace(' ', '+'), '&'])
        keywords = "".join(keywords)
        response = requests.get(f'https://quasimodo.r2.enst.fr/explorer/?{keywords}page={page}&order=pd')
        return response.text
    except:
        return ""


def extend_plural_and_singular(string: str,
                               engine: inflect.engine, 
                               list_to_update: Set[str]):
    plural = engine.plural(string)
    if plural and plural not in list_to_update:
        list_to_update.append(plural)

    singular = engine.singular_noun(string)
    if singular and singular not in list_to_update:
        list_to_update.append(singular)


def get_subject_props(subject: str, 
                      n_largest: int = 0,
                      verbose: bool = False,
                      plural_and_singular: bool = False) -> List[Tuple[str]]:
    subjects = [subject]
    if plural_and_singular:
        engine = inflect.engine()
        extend_plural_and_singular(subject, engine, subjects)

    matches = []
    matches_for_check = set()
    for sub in subjects:
        content = read_page({'subject': sub})
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find_all("table")
        if table:
            table = table[0] # assuming only one table in the page
        else:
            if verbose:
                secho(f"[WARNING] no match found for subject ({sub})", fg="yellow", bold=True)
            continue
        trs = table.find_all("tr")[1:]  # first row is the titles
        for tr in trs:
            tds = tr.find_all("td")
            if (tds[1].text, tds[2].text) not in matches_for_check:
                matches_for_check.add((tds[1].text, tds[2].text))
                matches.append((tds[0].text, tds[1].text.replace('_', ' '), tds[2].text, float(tds[5].text)))
    
    if n_largest > 0:
            matches = sorted(matches, key=lambda x: -x[3])
            matches = matches[:n_largest]

    if verbose:
        for match in matches:
            secho(f"{match[0]} ", fg="blue", bold=True, nl=False)
            secho(f"{match[1]} ", fg="green", bold=True, nl=False)
            secho(f"{match[2]}", fg="cyan", bold=True)

    return [(match[1], match[2]) for match in matches]


def get_subject_object_props(subject: str,
                             obj: str,
                             n_largest: int = 0,
                             verbose: bool = False,
                             plural_and_singular: bool = False) -> List[Tuple[str]]:

    subjects = [subject]
    objects = [obj]

    if plural_and_singular:
        engine = inflect.engine()
        extend_plural_and_singular(subject, engine, subjects)
        extend_plural_and_singular(obj, engine, objects)
    
    matches = []
    matches_for_check = set()
    for sub in subjects:
        for obj in objects:
            content = read_page({'subject': sub, 'object': obj})
            soup = BeautifulSoup(content, 'html.parser')
            table = soup.find_all("table")
            if table:
                table = table[0] # assuming only one table in the page
            else:
                if verbose:
                    secho(f"[WARNING] no match found for subject ({sub}) and object ({obj})", fg="yellow", bold=True)
                continue
            trs = table.find_all("tr")[1:]  # first row is the titles
            for tr in trs:
                tds = tr.find_all("td")
                if (tds[1].text, tds[2].text) not in matches_for_check:
                    matches_for_check.add((tds[1].text, tds[2].text))
                    matches.append((tds[0].text, tds[1].text.replace('_', ' '), tds[2].text, float(tds[5].text)))
    
    if n_largest > 0:
            matches = sorted(matches, key=lambda x: -x[3])
            matches = matches[:n_largest]

    if verbose:
        for match in matches:
            secho(f"{match[0]} ", fg="blue", bold=True, nl=False)
            secho(f"{match[1]} ", fg="green", bold=True, nl=False)
            secho(f"{match[2]}", fg="cyan", bold=True)

    return [match[1] for match in matches]


def get_number_of_results(soup: BeautifulSoup):
    div = soup.find_all('div', attrs={'class': 'container'})[0]
    p = div.find_all('p')
    if p:
        b = p[0].find_all('b') 
        if b:
            return int(b[0].text)
    return 0


def get_similarity_between_subjects(subject1: str,
                                    subject2: str,
                                    n_largest: int = 0,
                                    verbose: bool = False,
                                    plural_and_singular: bool = False) -> List[Tuple[str]]:

    subjects1 = [subject1]
    subjects2 = [subject2]

    if plural_and_singular:
        engine = inflect.engine()
        extend_plural_and_singular(subject1, engine, subjects1)
        extend_plural_and_singular(subject2, engine, subjects2)
    
    matches = []
    matches_for_check = {}

    for sub1 in subjects1:
        content = read_page({'subject': sub1})
        soup = BeautifulSoup(content, 'html.parser')
        number_of_results = get_number_of_results(soup)
        if number_of_results == 0:
            if verbose:
                secho(f"[WARNING] no match found for subject ({sub1})", fg="yellow", bold=True)
            continue
        
        for page in range(1, math.ceil(number_of_results / 20)):
            content = read_page({'subject': sub1}, page=page)
            soup = BeautifulSoup(content, 'html.parser')
            table = soup.find_all("table")[0]  # assuming only one table in the page
            trs = table.find_all("tr")[1:]  # first row is the titles
            for tr in trs:
                tds = tr.find_all("td")
                if (tds[1].text, tds[2].text) not in matches_for_check:
                    matches_for_check[(tds[1].text, tds[2].text)] = (tds[0].text, float(tds[5].text))

    for sub2 in subjects2:
        content = read_page({'subject': sub2})
        soup = BeautifulSoup(content, 'html.parser')
        number_of_results = get_number_of_results(soup)
        if number_of_results == 0:
            if verbose:
                secho(f"[WARNING] no match found for subject ({sub2})", fg="yellow", bold=True)
            continue
        
        for page in range(1, math.ceil(number_of_results / 20)):
            content = read_page({'subject': sub2}, page=page)
            soup = BeautifulSoup(content, 'html.parser')
            table = soup.find_all("table")[0]  # assuming only one table in the page
            trs = table.find_all("tr")[1:]  # first row is the titles
            for tr in trs:
                tds = tr.find_all("td")
                if (tds[1].text, tds[2].text) in matches_for_check:
                    matches.append((matches_for_check[(tds[1].text, tds[2].text)][0],
                                    tds[0].text,
                                    tds[1].text,
                                    tds[2].text,
                                    (matches_for_check[(tds[1].text, tds[2].text)][1] + float(tds[5].text)) / 2))
    
    if n_largest > 0:
            matches = sorted(matches, key=lambda x: -x[4])
            matches = matches[:n_largest]

    if verbose:
        for match in matches:
            secho(f"{match[0]} ", fg="blue", bold=True, nl=False)
            secho(f"and ", nl=False)
            secho(f"{match[1]} ", fg="blue", bold=True, nl=False)
            secho("are both ", nl=False)
            secho(f"{match[2]} ", fg="green", bold=True, nl=False)
            secho(f"{match[3]}", fg="cyan", bold=True)

    return [(match[2], match[3]) for match in matches]


def read_all_data(from_page: int = 1, to_page: int = 0):
    rows_list = []
    number_of_results = 3_845_266
    to_page = min(to_page, math.ceil(number_of_results / 20))
    for page in tqdm(range(from_page, to_page)):

        try:
            response = requests.get(f'https://quasimodo.r2.enst.fr/explorer/?page={page}')
            content = response.text
        except:
            secho(f"skipping page {page}")
            continue

        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find_all("table")[0]  # assuming only one table in the page
        trs = table.find_all("tr")[1:]  # first row is the titles
        for tr in trs:
            tds = tr.find_all("td")
            rows_list.append({
                "subject": tds[0].text,
                "predicate": tds[1].text,
                "object": tds[2].text,
                "plausibility": float(tds[5].text),
                "neighborhood_sigma": float(tds[6].text),
                "local_sigma": float(tds[7].text)
            })
    return rows_list

def write_tsv(from_page: int = 1, to_page: int = 0):
    info: List[Dict[str, str]] = read_all_data(from_page, to_page)
    df = DataFrame(info)

    dir_parent = Path('tsv')
    df.to_csv(dir_parent / f'{from_page}_{to_page}.tsv', sep="\t", index=False, encoding='utf-8')


def merge_tsvs(output: str):
    dir_parent = Path('tsv')
    dataframes = [pd.read_csv(path, sep="\t") for path in dir_parent.iterdir()]
    merged_df = pd.concat(dataframes)
    merged_df.to_csv(dir_parent / output, sep="\t", index=False, encoding='utf-8')


if __name__ == '__main__':
    # merge_tsvs('merged_df.tsv')

    start_page = 46000
    end_page = 50000
    print(start_page, end_page)
    write_tsv(start_page, end_page)

    # get_subject_props('horse', n_largest=20, verbose=True, plural_and_singular=True)
    # get_subject_object_props('sun', 'earth', n_largest=20, verbose=True, plural_and_singular=True)
    # get_similarity_between_subjects('sun', 'earth', n_largest=20, verbose=True, plural_and_singular=True)




    