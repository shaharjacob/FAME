from pathlib import Path

import pandas


class Quasimodo:

    def __init__(self, path: Path):
        self.data = self.init_data(path)
    
    def init_data(self, path: Path):
        COLUMNS_TO_REMOVE = ['saliency', 'typicality', 'sentences source', 'score', 'is_negative', 'modality']
        df = pandas.read_csv(path, sep='\t')
        for column in COLUMNS_TO_REMOVE:
            df.drop(column, axis='columns', inplace=True)
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
    

def main():
    quasimodo = Quasimodo('quasimodo43.tsv')
    a = quasimodo.filter_by_predicate_object('can', 'pause')
    print(a)

if __name__ == '__main__':
    main()