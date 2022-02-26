import copy
import json
from pathlib import Path
from collections import Counter
from typing import List, Union, Tuple

import inflect
import pandas as pd
from click import secho
from pandas import DataFrame

root = Path(__file__).resolve().parent.parent.parent

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

class Quasimodo:
    def __init__(self, path: Union[str, Path] = root / 'backend' / 'tsv' / 'merged' / 'quasimodo.tsv'):
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
        if not Path(path).exists():
            merge_tsvs()
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
    
    def get_entity_suggestions(self, entity: str, prop: str, n_largest: int = 0, plural_and_singular: bool = False):
        entities = [entity]
        if plural_and_singular:
            self.extend_plural_and_singular(entity, entities)
        
        # we filter by our entities, then we concat to one dataframe.
        subject_dataframes = [self.filter_by('subject', h) for h in entities]
        concat_subject_df = pd.concat(subject_dataframes)
        concat_subject_df = concat_subject_df.drop_duplicates(subset=['predicate', 'object'])
        filtered_df = self.filter_by('predicate', prop, use_outside_df=True, df=concat_subject_df)

        # plausibility is our messure for good match
        if n_largest:
            filtered_df = filtered_df.nlargest(n_largest, 'plausibility')

        return list(set([row['object'].replace('_', ' ') for _, row in filtered_df.iterrows()]))

    
    def filter_by(self, col: str, obj: str, inplace: bool = False, use_outside_df: bool = False, df: DataFrame = DataFrame(), n_largest: int = 0) -> DataFrame:
        if not use_outside_df:
            df = self.data if inplace else copy.deepcopy(self.data)
        df = df.dropna(subset=[col])
        df = df.loc[df[col] == obj]
        if n_largest > 0:
            df = df.nlargest(n_largest, 'plausibility')
        return df

    # def save_predicates(self):
    #     values = [val.replace("_", " ").lower() for val in self.data["predicate"].tolist()]
    #     dict_counter = Counter(values)
    #     d = {k: v for k, v in sorted(dict_counter.items(), key=lambda x: x[1], reverse=True)}
    #     with open('database/predicates.json', 'w') as f:
    #         json.dump(d, f, indent='\t')
    

def merge_tsvs(output: str = 'quasimodo.tsv'):
    tsv_folder = root / 'backend' / 'tsv'
    dataframes = [pd.read_csv(path, sep="\t") for path in (tsv_folder / 'parts').iterdir()]
    merged_df = pd.concat(dataframes)
    output_folder = tsv_folder / 'merged'
    if not output_folder.exists():
        output_folder.mkdir()
    merged_df.to_csv(output_folder / output, sep="\t", index=False, encoding='utf-8')


if __name__ == '__main__':
    merge_tsvs()
    # quasimodo = Quasimodo()
    # quasimodo.save_predicates()
    # values = list(predicates.values())
    # for prop in ["affect", "be considered", "different to", "look from other", "similar to the", "circle the", "move around", "orbit", "orbit the", "revolve around", "revolving around the", "spin around the", "stay around", "surround", "surround the", "travel around the"]:
    #     appearence = predicates.get(prop, 0)
    #     if appearence > 0:
    #         print(f"{prop}: {values.index(predicates.get(prop))}")
    #     else:
    #         prop = prop.replace(" ", "_")
    #         appearence = predicates.get(prop, 0)
    #         if appearence > 0:
    #             print(f"{prop}: {values.index(predicates.get(prop))}")
    #         else:
    #             print(f"not found ({prop})")
    # res = quasimodo.get_entity_props('sun', n_largest=5)
    # res = quasimodo.get_entities_relations('sun', 'earth', n_largest=5)
    # res = quasimodo.get_similarity_between_entities('horse', 'cow', n_largest=5)
    # print(res)
