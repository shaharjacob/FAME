import json
import copy
from pathlib import Path
from typing import List, Dict, Tuple, Set
from itertools import combinations

import inflect
import pandas as pd
from click import secho
from pandas import DataFrame


class Quasimodo:

    def __init__(self, 
                 path: str = 'quasimodo43.tsv', 
                 score_threshold: float = 0.9):

        self.data = self.init_data(path, score_threshold)
        self.engine = inflect.engine()
    

    def init_data(self, 
                  path: str, 
                  score_threshold: str) -> DataFrame:

        secho(f"[INFO] init Quasimodo data", fg='blue')
        df = pd.read_csv(path, sep='\t', low_memory=False)
        df.drop(df[df.score < score_threshold].index, inplace=True)
        df.drop_duplicates(inplace=True)
        return df
    

    def get_subject_props(self, 
                          subject: str, 
                          n_largest: int = 0,
                          plural_and_singular: bool = False) -> List[Tuple[str]]:

        def add_to_set(subject_: str, set_to_add: Set[Tuple]):
            df = self.filter_by('subject', subject_)
            for _, val in df.iterrows():
                set_to_add.add((str(val['predicate']).replace('_', ' '), 
                               str(val['object']), 
                               val['score']))

        props_set = set()
        add_to_set(subject, props_set)

        if plural_and_singular:
            plural = self.engine.plural(subject)
            if plural and plural != subject:
                add_to_set(plural, props_set)

            singular = self.engine.singular_noun(subject)
            if singular and singular != subject and singular != plural:
                add_to_set(singular, props_set)

        props_list = list(props_set)
        if n_largest > 0:
            props_list = sorted(props_list, key=lambda x: -x[2])
            props_list = props_list[:n_largest]

        return [(prop[0], prop[1]) for prop in props_list]


    def get_subject_object_props(self,
                                 subject: str,
                                 obj: str,
                                 n_largest: int = 0,
                                 plural_and_singular: bool = False) -> List[Tuple[str]]:
        
        def add_to_set(subject_: str, obj_: str, set_to_add: Set[Tuple]):
            df = self.filter_by('subject', subject_)
            df = self.filter_by('object', obj_, use_outside_df=True, df=df)

            for _, val in df.iterrows():
                set_to_add.add((str(val['predicate']).replace('_', ' '),
                               val['score']))

        def extend_list(string: str, list_to_add: List[str]):
            plural = self.engine.plural(string)
            if plural and (plural not in list_to_add):
                list_to_add.append(plural)

            singular = self.engine.singular_noun(string)
            if singular and (singular not in list_to_add):
                list_to_add.append(singular)

        props_set = set()
        subjects = [subject]
        objects = [obj]

        if plural_and_singular:
            extend_list(subject, subjects)
            extend_list(obj, objects)
        
        for subject_ in subjects:
            for obj_ in objects:
                add_to_set(subject_, obj_, props_set)
        
        props_list = list(props_set)
        if n_largest > 0:
            props_list = sorted(props_list, key=lambda x: -x[1])
            props_list = props_list[:n_largest]

        return [prop[0] for prop in props_list]


    def get_similarity_between_subjects(self,
                                        subject1: str,
                                        subject2: str) -> List[Tuple[str]]:

        data_of_subject1 = self.filter_by('subject', subject1)
        data_of_subject2 = self.filter_by('subject', subject2)
        predicate_obj_of_subject1 = set()
        matches = set()
        for _, val1 in data_of_subject1.iterrows():
            if val1['predicate'] and val1['object']:
                predicate_obj_of_subject1.add((val1['predicate'], val1['object']))
        for _, val2 in data_of_subject2.iterrows():
            if (val2['predicate'], val2['object']) in predicate_obj_of_subject1:
                matches.add((val2['predicate'].replace('_', ' '), val2['object']))

        return list(matches)

    
    def filter_by(self, 
                  col: str,
                  obj: str, 
                  soft: bool = False, 
                  use_outside_df: bool = False,
                  df: DataFrame = DataFrame(), 
                  n_largest: int = 0) -> DataFrame:

        if not use_outside_df:
            df = copy.deepcopy(self.data)
        df.dropna(subset=[col], inplace=True)
        if soft:
            df = df[df[col].str.contains(obj)]
        else:
            df = df.loc[df[col] == obj]
        if n_largest > 0:
            df = df.nlargest(n_largest, 'score')
        return df

    
if __name__ == '__main__':
    quasimodo = Quasimodo(path='quasimodo_0.5.tsv', score_threshold=0.5)
    res1 = quasimodo.get_subject_props('horses', n_largest=10)
    res2 = quasimodo.get_subject_object_props('horses', 'stables', n_largest=10)
    res3 = quasimodo.get_similarity_between_subjects('horse', 'cow')



    