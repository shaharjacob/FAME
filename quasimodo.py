import json
from pathlib import Path

import pandas
from tqdm import tqdm
from click import secho


class Quasimodo:

    def __init__(self, path: str = 'quasimodo43.tsv', score_threshold: float = 0.9, save_ordered: bool = True):
        self.data = self.init_data(path, score_threshold)
        self.predicates = set()
        self.subjects = set()
        self.objects = set()
        # self.pairs = {}
        # self.save_paris()
        if save_ordered:
            self.save_ordered_entries()
    

    def init_data(self, path: str, score_threshold: str):
        secho(f"[INFO] init data", fg='blue')
        df = pandas.read_csv(path, sep='\t')
        df.drop(df[df.score < score_threshold].index, inplace=True)
        df.drop_duplicates(inplace=True)
        return df
    

    def filter_by_subject(self, subject: str):
        return self.data.loc[self.data['subject'] == subject]
    

    def filter_by_predicate(self, predicate: str):
        return self.data.loc[self.data['predicate'] == predicate]
    

    def filter_by_object(self, obj: str):
        return self.data.loc[self.data['object'] == obj]
    

    def filter_by_predicate_object(self, predicate: str, obj: str):
        return self.data.loc[(self.data['predicate'] == predicate) & (self.data['object'] == obj)]
    

    # def save_paris(self, path: str = 'pairs.json'):
    #     if not Path(path).exists():
    #         secho(f"[INFO] Saving pairs into {path}", fg='blue')
    #         percent = 1
    #         for idx, val in self.data.iterrows():
    #             if (idx / len(self.data)) * 100 > percent:
    #                 secho(f"{percent}% complete", fg='blue')
    #                 percent += 1
    #             if f"{val['predicate']}:{val['object']}" not in self.pairs:
    #                 self.pairs[f"{val['predicate']}:{val['object']}"] = set()
    #             self.pairs[f"{val['predicate']}:{val['object']}"].add(val['subject'])
                
    #         for key, value in self.pairs.items():
    #             self.pairs[key] = list(value) # set is not serializable
    #         with open(path, 'w') as fp:
    #             json.dump(self.pairs, fp)
    #     else:
    #         secho(f"[INFO] Loading pairs from {path}", fg='blue')
    #         self.pairs = json.loads(Path(path).read_text())


    def save_ordered_entries(self, predicates_path: str = 'predicates.json', subjects_path: str = 'subjects.json', objects_path: str = 'objects.json'):
        if not Path(predicates_path).exists or \
            not Path(subjects_path).exists or \
            not Path(objects_path).exists:
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
            self.objects = sorted(list(self.objects))
            with open(predicates_path, 'w') as fp:
                json.dump({"predicates": self.predicates}, fp)
            with open(subjects_path, 'w') as fp:
                json.dump({"subjects": self.subjects}, fp)
            with open(objects_path, 'w') as fp:
                json.dump({"objects": self.objects}, fp)
        else:
            secho(f"[INFO] Loading predicates from {predicates_path}", fg='blue')
            self.predicates = json.loads(Path(predicates_path).read_text())['predicates']
            secho(f"[INFO] Loading subjects from {subjects_path}", fg='blue')
            self.subjects = json.loads(Path(subjects_path).read_text())['subjects']
            secho(f"[INFO] Loading objects from {objects_path}", fg='blue')
            self.objects = json.loads(Path(objects_path).read_text())['objects']

    
    def get_subject_predicates(self, subject1: str, subject2: str):
        data_of_subject1 = self.filter_by_subject(subject1)
        data_of_subject2 = self.filter_by_subject(subject2)
        predicate_obj_of_subject1 = set()
        matches = set()
        for _, val1 in data_of_subject1.iterrows():
            predicate_obj_of_subject1.add(f"{val1['predicate']}:{val1['object']}")
        for _, val2 in data_of_subject2.iterrows():
            if f"{val2['predicate']}:{val2['object']}" in predicate_obj_of_subject1:
                matches.add(f"{val2['predicate']}:{val2['object']}")
        return matches
    
if __name__ == '__main__':
    quasimodo = Quasimodo(score_threshold=0.9)
    matches = quasimodo.get_subject_predicates('horse', 'cow')
    print(matches)

