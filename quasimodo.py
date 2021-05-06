import math
import copy
from pathlib import Path
from typing import List, Dict, Tuple

import inflect
import requests
import pandas as pd
from tqdm import tqdm
from click import secho
from pandas import DataFrame
from bs4 import BeautifulSoup


class Quasimodo:

    def __init__(self, 
                 path: str = 'merged.tsv'):

        self.data = self.init_data(path)
        self.engine = inflect.engine()
    

    def extend_plural_and_singular(self,
                                   string: str,
                                   list_to_update: List[str]):

        plural = self.engine.plural(string)
        if plural and plural not in list_to_update:
            list_to_update.append(plural)

        singular = self.engine.singular_noun(string)
        if singular and singular not in list_to_update:
            list_to_update.append(singular)
    

    def init_data(self, 
                  path: str) -> DataFrame:

        secho(f"[INFO] init Quasimodo data", fg='blue')
        return pd.read_csv(path, sep='\t', low_memory=False)
    

    def get_subject_props(self, 
                          subject: str, 
                          n_largest: int = 0,
                          verbose: bool = False,
                          plural_and_singular: bool = False) -> List[Tuple[str]]:
        
        subjects = [subject]
        if plural_and_singular:
            self.extend_plural_and_singular(subject, subjects)
        
        dataframes = [self.filter_by('subject', s) for s in subjects]
        concat_df = pd.concat(dataframes)
        concat_df = concat_df.drop_duplicates(subset=['predicate', 'object'])

        if n_largest:
            concat_df = concat_df.nlargest(n_largest, 'plausibility')

        props_list = []
        for _, val in concat_df.iterrows():
            props_list.append((val['predicate'].replace('_', ' '), val['object']))
            if verbose:
                secho(f"{val['subject']} ", fg="blue", bold=True, nl=False)
                secho(f"{val['predicate'].replace('_', ' ')} ", fg="green", bold=True, nl=False)
                secho(f"{val['object']} ", fg="cyan", bold=True, nl=False)
                current_length = len(val['subject']) + len(val['predicate']) + len(val['object']) + 2
                max_length = 40
                spaces = ' '.join([""] * max(1, (max_length - current_length)))
                secho(f"{spaces}score: ", nl=False)
                secho(f"{val['plausibility']}", fg="magenta")

        return props_list

    
    def get_subject_object_props(self, 
                                 subject: str, 
                                 obj: str,
                                 n_largest: int = 0,
                                 verbose: bool = False,
                                 plural_and_singular: bool = False) -> List[Tuple[str]]:
        
        subjects = [subject]
        objects = [obj]
        if plural_and_singular:
            self.extend_plural_and_singular(subject, subjects)
            self.extend_plural_and_singular(obj, objects)
        
        subject_dataframes = [self.filter_by('subject', s) for s in subjects]
        concat_subject_df = pd.concat(subject_dataframes)
        concat_subject_df = concat_subject_df.drop_duplicates(subset=['predicate', 'object'])

        filtered_dataframes = [self.filter_by('object', o, use_outside_df=True, df=concat_subject_df) for o in objects]
        concat_filtered_df = pd.concat(filtered_dataframes)
        concat_filtered_df = concat_filtered_df.drop_duplicates(subset=['predicate', 'object'])

        if n_largest:
            concat_filtered_df = concat_filtered_df.nlargest(n_largest, 'plausibility')

        props_list = []
        for _, val in concat_filtered_df.iterrows():
            props_list.append(val['predicate'].replace('_', ' '))
            if verbose:
                secho(f"{val['subject']} ", fg="blue", bold=True, nl=False)
                secho(f"{val['predicate'].replace('_', ' ')} ", fg="green", bold=True, nl=False)
                secho(f"{val['object']} ", fg="cyan", bold=True, nl=False)
                current_length = len(val['subject']) + len(val['predicate']) + len(val['object']) + 2
                max_length = 40
                spaces = ' '.join([""] * max(1, (max_length - current_length)))
                secho(f"{spaces}score: ", nl=False)
                secho(f"{val['plausibility']}", fg="magenta")

        return props_list


    def get_similarity_between_subjects(self,
                                        subject1: str,
                                        subject2: str,
                                        n_largest: int = 0,
                                        verbose: bool = False,
                                        plural_and_singular: bool = False) -> List[Tuple[str]]:
        
        subjects1 = [subject1]
        subjects2 = [subject2]

        if plural_and_singular:
            self.extend_plural_and_singular(subject1, subjects1)
            self.extend_plural_and_singular(subject2, subjects2)
        
        subject1_dataframes = [self.filter_by('subject', s) for s in subjects1]
        concat_subject1_df = pd.concat(subject1_dataframes)
        concat_subject1_df = concat_subject1_df.drop_duplicates(subset=['predicate', 'object'])

        subject2_dataframes = [self.filter_by('subject', s) for s in subjects2]
        concat_subject2_df = pd.concat(subject2_dataframes)
        concat_subject2_df = concat_subject2_df.drop_duplicates(subset=['predicate', 'object'])

        concat_df = pd.concat([concat_subject1_df, concat_subject2_df])
        df = concat_df[['predicate','object']]
        df = df[df.duplicated(keep=False)]
        if df.empty:
            return []
            
        indexies = df.groupby(list(df)).apply(lambda x: tuple(x.index)).tolist()
        matches = []
        for index in indexies:
            sub1_row = concat_df.loc[index[0]]
            sub2_row = concat_df.loc[index[1]]
            matches.append({
                "predicate": sub1_row['predicate'],
                "object": sub1_row['object'],
                "plausibility": (sub1_row['plausibility'] + sub2_row['plausibility']) / 2,
            })

        new_df = DataFrame(matches)
        new_df = new_df.drop_duplicates(subset=['predicate', 'object'])

        if n_largest:
            new_df = new_df.nlargest(n_largest, 'plausibility')

        props_list = []
        for _, val in new_df.iterrows():
            props_list.append((val['predicate'].replace('_', ' '), val['object']))
            if verbose:
                secho(f"{subject1} ", fg="blue", bold=True, nl=False)
                secho(f"and ", nl=False)
                secho(f"{subject2} ", fg="blue", bold=True, nl=False)
                secho("are both ", nl=False)
                secho(f"{val['predicate'].replace('_', ' ')} ", fg="green", bold=True, nl=False)
                secho(f"{val['object']}", fg="cyan", bold=True, nl=False)
                current_length = len(f"{subject1} ") + len("and ") + len(f"{subject2} ") + len("are both ") + len(f"{val['predicate']} ") + len(val['object'])
                max_length = 50
                spaces = ' '.join([""] * max(1, (max_length - current_length)))
                secho(f"{spaces}avg. score: ", nl=False)
                secho(f"{val['plausibility']}", fg="magenta")

        return props_list

    
    def filter_by(self, 
                  col: str,
                  obj: str, 
                  inplace: bool = False,
                  use_outside_df: bool = False,
                  df: DataFrame = DataFrame(), 
                  n_largest: int = 0) -> DataFrame:

        if not use_outside_df:
            df = self.data if inplace else copy.deepcopy(self.data)
        df = df.dropna(subset=[col])
        df = df.loc[df[col] == obj]
        if n_largest > 0:
            df = df.nlargest(n_largest, 'plausibility')
        return df


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
    pass
    # merge_tsvs('quasimodo.tsv')

    # start_page = 48000
    # end_page = 50000
    # print(start_page, end_page)
    # write_tsv(start_page, end_page)

    # quasimodo = Quasimodo(path='tsv/merged_df.tsv')
    # quasimodo.get_subject_props('cow', 100, True, True)
    # quasimodo.get_subject_object_props('cow', 'milk', 7, True, True)
    # quasimodo.get_similarity_between_subjects('cow', 'chicken', 100, True, True)



    