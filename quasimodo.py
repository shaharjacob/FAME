import json
import copy
from pathlib import Path
from typing import List, Dict
from itertools import combinations

import pandas as pd
from click import secho
from pandas import DataFrame


class Quasimodo:

    def __init__(self, path: str = 'quasimodo43.tsv', score_threshold: float = 0.9, save_ordered: bool = False):
        self.data = self.init_data(path, score_threshold)
        self.predicates = set()
        self.subjects = set()
        self.objects = set()
        if save_ordered:
            self.save_ordered_entries()
    

    def init_data(self, path: str, score_threshold: str) -> DataFrame:
        secho(f"[INFO] init data", fg='blue')
        df = pd.read_csv(path, sep='\t', low_memory=False)
        df.drop(df[df.score < score_threshold].index, inplace=True)
        df.drop_duplicates(inplace=True)
        return df
    

    def filter_by_subject(self, subject: str, soft: bool = False, df: DataFrame = DataFrame()) -> DataFrame:
        df = copy.deepcopy(self.data) if df.empty else df
        df.dropna(subset=["subject"], inplace=True)
        if soft:
            return df[df['subject'].str.contains(subject)]
        else:
            return df.loc[df['subject'] == subject]
    

    def filter_by_predicate(self, predicate: str, soft: bool = False, df: DataFrame = DataFrame()) -> DataFrame:
        df = copy.deepcopy(self.data) if df.empty else df
        df.dropna(subset=["predicate"], inplace=True)
        if soft:
            return df[df['predicate'].str.contains(predicate)]
        else:
            return df.loc[df['predicate'] == predicate]
    

    def filter_by_object(self, obj: str, soft: bool = False, df: DataFrame = DataFrame()) -> DataFrame:
        df = copy.deepcopy(self.data) if df.empty else df
        df.dropna(subset=["object"], inplace=True)
        if soft:
            return df[df['object'].str.contains(obj)] # TODO: using difflib.get_close_matches
        else:
            return df.loc[df['object'] == obj]
    

    def get_all_objects_of_a_subject(self, subject: str) -> List[str]:
        df = self.filter_by_subject(subject)
        return df["object"].to_list()
    

    def get_all_predicates_of_a_subject(self, subject: str) -> List[str]:
        df = self.filter_by_subject(subject)
        return df["predicate"].to_list()


    def save_ordered_entries(self, predicates_path: str = 'predicates.json', subjects_path: str = 'subjects.json', objects_path: str = 'objects.json'):
        if not Path(predicates_path).exists() or not Path(subjects_path).exists() or not Path(objects_path).exists():
            self.predicates = set()
            self.subjects = set()
            self.objects = set()
            percent = 1
            for idx, val in self.data.iterrows():
                if (idx / len(self.data)) * 100 > percent:
                    secho(f"{percent}% complete", fg='blue')
                    percent += 1

                self.predicates.add(str(val['predicate']))
                self.subjects.add(str(val['subject']))
                self.objects.add(str(val['object']))

            self.predicates = sorted(list(self.predicates))
            self.subjects = sorted(list(self.subjects))
            for i, subject in enumerate(self.subjects):
                if subject[0] == 'a':
                    self.subjects = self.subjects[i:]
                    break
            self.objects = sorted(list(self.objects))
            for i, obj in enumerate(self.objects):
                if obj[0] == 'a':
                    self.objects = self.objects[i:]
                    break
            with open(predicates_path, 'w') as f1:
                json.dump({"predicates": self.predicates}, f1)
            with open(subjects_path, 'w') as f2:
                json.dump({"subjects": self.subjects}, f2)
            with open(objects_path, 'w') as f3:
                json.dump({"objects": self.objects}, f3)
        else:
            self.predicates = json.loads(Path(predicates_path).read_text())['predicates']
            self.subjects = json.loads(Path(subjects_path).read_text())['subjects']
            self.objects = json.loads(Path(objects_path).read_text())['objects']


    def get_connections_between_subjects(self, arr: List[str], soft: bool = False) -> Dict[str, List[str]]:
        combs = list(combinations(arr, 2))
        results = {}
        for comb in combs:
            results.update(self.get_connections_between_pairs_of_subjects(comb[0], comb[1], soft=soft))

        for key, value in results.items():
            secho(key, fg="blue", bold=True)
            for match in value:
                secho(f"- {match}", fg="blue")
            print()
        
        matches = set()
        init = True
        for key, value in results.items():
            if init:
                matches = set(value)
                init = False
            else:
                matches = matches & set(value)
        secho("Common:", fg="blue", bold=True)
        for match in matches:
            secho(f"- {match}", fg="blue")
        print()

        return results

    
    def get_connections_between_pairs_of_subjects(self, subject1: str, subject2: str, soft: bool = False) -> Dict[str, List[str]]:
        data_of_subject1 = self.filter_by_subject(subject1, soft=soft)
        data_of_subject2 = self.filter_by_subject(subject2, soft=soft)
        predicate_obj_of_subject1 = set()
        matches = set()
        for _, val1 in data_of_subject1.iterrows():
            if val1['predicate'] and val1['object']:
                predicate_obj_of_subject1.add(f"{val1['predicate']}:{val1['object']}")
        for _, val2 in data_of_subject2.iterrows():
            if f"{val2['predicate']}:{val2['object']}" in predicate_obj_of_subject1:
                matches.add(f"{val2['predicate']}:{val2['object']}")

        return {
            f"{subject1} ~ {subject2}": list(matches)
        }
    

    def get_connections(self, arr: List[str], soft: bool = False) -> List[Dict[str, str]]:
        combs = list(combinations(arr, 2))
        results = []
        for comb in combs:
            results.extend(self.get_connections_of_pair(comb[0], comb[1], soft=soft))
            results.extend(self.get_connections_of_pair(comb[1], comb[0], soft=soft))

        for result in results:
            secho(f"{result['subject']} ", fg="blue", bold=True, nl=False)
            secho(f"{result['predicate']} ", fg="green", bold=True, nl=False)
            secho(result["object"], fg="cyan", bold=True)

        return results


    def get_connections_of_pair(self, subject: str, obj: str, soft: bool = False) -> List[Dict[str, str]]:
        df = self.filter_by_subject(subject, soft=soft)
        df = self.filter_by_object(obj, soft=soft, df=df)
        return df.to_dict('records')


    def get_all_closest_subject(self, subject: str) -> List[str]:
        return [subject_ for subject_ in self.subjects if subject in subject_]

    
    def get_all_closest_objects(self, obj: str) -> List[str]:
        return [obj_ for obj_ in self.objects if obj in obj_]

    
if __name__ == '__main__':
    quasimodo = Quasimodo(score_threshold=0.9)
    # quasimodo.get_connections(["sharp", "needle", "knife"], soft=True)
    quasimodo.get_connections(["sharp", "needle", "knife"])
    # quasimodo.get_connections_between_subjects(["horse", "cow", "chicken"])
    # quasimodo.get_connections_between_subjects(["horse", "cow", "chicken"], soft=True)

