import math
import copy
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple

import inflect
import requests
import pandas as pd
from tqdm import tqdm
from click import secho
from pandas import DataFrame
from bs4 import BeautifulSoup


class Quasimodo:
    def __init__(self, path: str = 'tsv/quasimodo.tsv'):
        self.data = self.init_data(path)
        self.engine = inflect.engine()
    
    def extend_plural_and_singular(self, string: str, list_to_update: List[str]):
        plural = self.engine.plural(string)
        if plural and plural not in list_to_update:
            list_to_update.append(plural)

        singular = self.engine.singular_noun(string)
        if singular and singular not in list_to_update:
            list_to_update.append(singular)
    
    def init_data(self, path: str) -> DataFrame:
        secho(f"[INFO] init Quasimodo data", fg='blue')
        return pd.read_csv(path, sep='\t', low_memory=False)
    
    def get_entity_props(self, entity: str, n_largest: int = 10, verbose: bool = False, plural_and_singular: bool = False) -> List[Tuple[str]]:
        entities = [entity]
        # first we extend to plural and singular
        if plural_and_singular:
            self.extend_plural_and_singular(entity, entities)
        
        # now we will filter by the entities and concat all to one dataframe.
        dataframes = [self.filter_by('subject', s) for s in entities]
        concat_df = pd.concat(dataframes)
        concat_df = concat_df.drop_duplicates(subset=['predicate', 'object'])
        
        # plausibility is our messure for good match
        if n_largest:
            concat_df = concat_df.nlargest(n_largest, 'plausibility')

        props_list = []
        for _, row in concat_df.iterrows():
            props_list.append((row['predicate'].replace('_', ' '), row['object']))
            if verbose:
                render(row)
        return props_list

    def get_entities_relations(self, entity1: str, entity2: str, n_largest: int = 0, verbose: bool = False, plural_and_singular: bool = False) -> List[Tuple[str]]:
        entities1 = [entity1]
        entities2 = [entity2]
        # first we extend to plural and singular
        if plural_and_singular:
            self.extend_plural_and_singular(entity1, entities1)
            self.extend_plural_and_singular(entity2, entities2)
        
        # we filter by our entities1, then we concat to one dataframe.
        subject_dataframes = [self.filter_by('subject', h) for h in entities1]
        concat_subject_df = pd.concat(subject_dataframes)
        concat_subject_df = concat_subject_df.drop_duplicates(subset=['predicate', 'object'])

        # the filtered dataframe (by entities1), we filter again with entities2, then we again concat to one dataframe.
        filtered_dataframes = [self.filter_by('object', t, use_outside_df=True, df=concat_subject_df) for t in entities2]
        concat_filtered_df = pd.concat(filtered_dataframes)
        concat_filtered_df = concat_filtered_df.drop_duplicates(subset=['predicate', 'object'])

        # plausibility is our messure for good match
        if n_largest:
            concat_filtered_df = concat_filtered_df.nlargest(n_largest, 'plausibility')

        props_list = []
        for _, row in concat_filtered_df.iterrows():
            props_list.append(row['predicate'].replace('_', ' '))
            if verbose:
                render(row)

        return props_list

    def get_similarity_between_entities(self, entity1: str, entity2: str, n_largest: int = 0, verbose: bool = False, plural_and_singular: bool = False) -> List[Tuple[str]]:
        entities1 = [entity1]
        entities2 = [entity2]
        # first we extend to plural and singular
        if plural_and_singular:
            self.extend_plural_and_singular(entity1, entities1)
            self.extend_plural_and_singular(entity2, entities2)
        
        # we now filter by the first entity
        entity1_dataframes = [self.filter_by('subject', n1) for n1 in entities1]
        concat_entity1_df = pd.concat(entity1_dataframes)
        concat_entity1_df = concat_entity1_df.drop_duplicates(subset=['predicate', 'object'])

        # we now filter by the second entity
        entity2_dataframes = [self.filter_by('subject', n2) for n2 in entities2]
        concat_entity2_df = pd.concat(entity2_dataframes)
        concat_entity2_df = concat_entity2_df.drop_duplicates(subset=['predicate', 'object'])

        # https://stackoverflow.com/questions/22219004/how-to-group-dataframe-rows-into-list-in-pandas-groupby
        concat_df = pd.concat([concat_entity1_df, concat_entity2_df])
        df = concat_df[['predicate','object']]
        df = df[df.duplicated(keep=False)]
        if df.empty:
            return []
            
        indexies = df.groupby(list(df)).apply(lambda x: tuple(x.index)).tolist()
        matches = []
        for index in indexies:
            entity1_row = concat_df.loc[index[0]]
            entity2_row = concat_df.loc[index[1]]
            matches.append({
                "predicate": entity1_row['predicate'],
                "object": entity1_row['object'],
                "plausibility": (entity1_row['plausibility'] + entity2_row['plausibility']) / 2,
            })

        new_df = DataFrame(matches)
        new_df = new_df.drop_duplicates(subset=['predicate', 'object'])

        if n_largest:
            new_df = new_df.nlargest(n_largest, 'plausibility')

        props_list = []
        for _, row in new_df.iterrows():
            props_list.append((row['predicate'].replace('_', ' '), row['object']))
            if verbose:
                render_entities_similarity(entity1, entity2, row)
        return props_list
    
    def filter_by(self, col: str, obj: str, inplace: bool = False, use_outside_df: bool = False, df: DataFrame = DataFrame(), n_largest: int = 0) -> DataFrame:
        if not use_outside_df:
            df = self.data if inplace else copy.deepcopy(self.data)
        df = df.dropna(subset=[col])
        df = df.loc[df[col] == obj]
        if n_largest > 0:
            df = df.nlargest(n_largest, 'plausibility')
        return df


def render(row: dict):
    secho(f"{row['subject']} ", fg="blue", bold=True, nl=False)
    secho(f"{row['predicate'].replace('_', ' ')} ", fg="green", bold=True, nl=False)
    secho(f"{row['object']} ", fg="cyan", bold=True, nl=False)
    current_length = len(row['subject']) + len(row['predicate']) + len(row['object']) + 2
    max_length = 40
    spaces = ' '.join([""] * max(1, (max_length - current_length)))
    secho(f"{spaces}score: ", nl=False)
    secho(f"{row['plausibility']}", fg="magenta")


def render_entities_similarity(entity1: str, entity2: str, row: dict):
    secho(f"{entity1} ", fg="blue", bold=True, nl=False)
    secho(f"and ", nl=False)
    secho(f"{entity2} ", fg="blue", bold=True, nl=False)
    secho("are both ", nl=False)
    secho(f"{row['predicate'].replace('_', ' ')} ", fg="green", bold=True, nl=False)
    secho(f"{row['object']}", fg="cyan", bold=True, nl=False)
    current_length = len(f"{entity1} ") + len("and ") + len(f"{entity2} ") + len("are both ") + len(f"{row['predicate']} ") + len(row['object'])
    max_length = 50
    spaces = ' '.join([""] * max(1, (max_length - current_length)))
    secho(f"{spaces}avg. score: ", nl=False)
    secho(f"{row['plausibility']}", fg="magenta")


def merge_tsvs(output: str):
    dir_parent = Path('tsv')
    dataframes = [pd.read_csv(path, sep="\t") for path in dir_parent.iterdir()]
    merged_df = pd.concat(dataframes)
    merged_df.to_csv(dir_parent / output, sep="\t", index=False, encoding='utf-8')


if __name__ == '__main__':
    quasimodo = Quasimodo()
    quasimodo.get_entity_props("faraday", n_largest=5, verbose=True)
















# def count_predicates(self, n: int = 0):
#     if n > 0:
#         return Counter(self.data["predicate"].tolist()).most_common(n)
#     return Counter(self.data["predicate"].tolist())

# def count_pred_obj_paris(self, n: int = 0):
#     predicates = self.data["predicate"].tolist()
#     objects = self.data["object"].tolist()
#     concat = [(predicate, obj) for predicate, obj in zip(predicates, objects)]
#     if n > 0:
#         return Counter(concat).most_common(n)
#     return Counter(concat)

# def read_all_data(from_page: int = 1, to_page: int = 0):
#     rows_list = []
#     number_of_results = 3_845_266
#     to_page = min(to_page, math.ceil(number_of_results / 20))
#     for page in tqdm(range(from_page, to_page)):

#         try:
#             response = requests.get(f'https://quasimodo.r2.enst.fr/explorer/?page={page}')
#             content = response.text
#         except:
#             secho(f"skipping page {page}")
#             continue

#         soup = BeautifulSoup(content, 'html.parser')
#         table = soup.find_all("table")[0]  # assuming only one table in the page
#         trs = table.find_all("tr")[1:]  # first row is the titles
#         for tr in trs:
#             tds = tr.find_all("td")
#             rows_list.append({
#                 "subject": tds[0].text,
#                 "predicate": tds[1].text,
#                 "object": tds[2].text,
#                 "plausibility": float(tds[5].text),
#                 "neighborhood_sigma": float(tds[6].text),
#                 "local_sigma": float(tds[7].text)
#             })
#     return rows_list


# def write_tsv(from_page: int = 1, to_page: int = 0):
#     info: List[Dict[str, str]] = read_all_data(from_page, to_page)
#     df = DataFrame(info)
#     dir_parent = Path('tsv')
#     df.to_csv(dir_parent / f'{from_page}_{to_page}.tsv', sep="\t", index=False, encoding='utf-8')


