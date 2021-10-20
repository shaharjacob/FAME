import os
import json
from typing import List
from pathlib import Path

from click import secho

from utils import utils
from . import openIE
from . import mapping
from . import google_autosuggest
from .quasimodo import Quasimodo
from frequency.frequency import Frequencies
from .data_collector import DataCollector
from utils.sentence_embadding import SentenceEmbedding

root = Path(__file__).resolve().parent.parent.parent

IGNORE_SUGGESTION = ["the", "they", "us", "we", "you", 'i']

class Suggestions(object):
    def __init__(self, entity: str, prop: str, save_db: bool = True, override_database: bool = False, quasimodo: Quasimodo = None):
        self.entity = entity
        self.prop = prop
        self.quasimodo = quasimodo
        self.override_database = override_database
        self.save_db = save_db
        self.google_suggestinos = utils.read_json(root / 'backend' / 'database' / 'google_suggestinos.json') if save_db else {}
        self.quasimodo_suggestinos = utils.read_json(root / 'backend' / 'database' / 'quasimodo_suggestinos.json') if save_db else {}
        self.openie_suggestinos = utils.read_json(root / 'backend' / 'database' / 'openie_suggestinos.json') if save_db else {}
    

    def get_suggestions(self):
        should_save = False
        if f"{self.entity}#{self.prop}" in self.google_suggestinos and not self.override_database:
            google_suggestinos = self.google_suggestinos[f"{self.entity}#{self.prop}"]
        else:
            google_suggestinos = google_autosuggest.get_entity_suggestions(self.entity, self.prop)
            self.google_suggestinos[f"{self.entity}#{self.prop}"] = google_suggestinos  
            should_save = True
        
        if f"{self.entity}#{self.prop}" in self.quasimodo_suggestinos and not self.override_database:
            quasimodo_suggestinos = self.quasimodo_suggestinos[f"{self.entity}#{self.prop}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo()
            quasimodo_suggestinos = self.quasimodo.get_entity_suggestions(self.entity, self.prop, n_largest=5, plural_and_singular=True)
            self.quasimodo_suggestinos[f"{self.entity}#{self.prop}"] = quasimodo_suggestinos  
            should_save = True
        
        if f"{self.entity}#{self.prop}" in self.openie_suggestinos and not self.override_database:
            openie_suggestinos = self.openie_suggestinos[f"{self.entity}#{self.prop}"]
        else:
            openie_suggestinos = openIE.get_entity_suggestions_wrapper(self.entity, self.prop, n_largest=5)
            self.openie_suggestinos[f"{self.entity}#{self.prop}"] = openie_suggestinos  
            should_save = True

        if should_save:
            self.save_database()

        suggestions = list(set(google_suggestinos + quasimodo_suggestinos)) # + openie_suggestinos
        return [suggestion for suggestion in suggestions if suggestion not in IGNORE_SUGGESTION]


    def save_database(self):
        with open(root / 'backend' / 'database' / 'google_suggestinos.json', 'w') as f1:
            json.dump(self.google_suggestinos, f1, indent='\t')
        with open(root / 'backend' / 'database' / 'quasimodo_suggestinos.json', 'w') as f2:
            json.dump(self.quasimodo_suggestinos, f2, indent='\t')
        with open(root / 'backend' / 'database' / 'openie_suggestinos.json', 'w') as f3:
            json.dump(self.openie_suggestinos, f3, indent='\t')


def get_suggestions_for_missing_entities(data_collector: DataCollector, 
                                         base_not_mapped_entity: str, 
                                         base_already_mapping: List[str], 
                                         target_already_mapping: List[str], 
                                         verbose: bool = False
                                         ) -> List[str]:
    suggests_list = []
    # we need all the relations between the entity (the one that not mapped) to the entities that already mapped (again - in the same domain)
    for idx, base_entity in enumerate(base_already_mapping):
        if verbose: 
            secho(f"(^{base_not_mapped_entity}, {base_entity})", fg="blue", bold=True)

        props_entity_1 = data_collector.get_entities_relations(base_entity, base_not_mapped_entity)
        props_entity_2 = data_collector.get_entities_relations(base_not_mapped_entity, base_entity)

        # we we use the map that we already know (base_entity->target_already_mapping[idx])
        if verbose: 
            secho(f"  {target_already_mapping[idx]}", fg="red", bold=True)
        for prop in set(props_entity_1 + props_entity_2):
            suggestions_model = Suggestions(target_already_mapping[idx], prop, quasimodo=data_collector.quasimodo)
            props = suggestions_model.get_suggestions()
            if props:
                # we found candidates for '<exist_entity> <prop> <candidate>' or '<candidate> <prop> <exist_entity>'
                suggests_list.extend(props)
                if verbose:
                    secho(f"    {prop}: ", fg="green", bold=True, nl=False)
                    secho(f"{props}", fg="cyan")
        if verbose: 
            if not props_entity_1 + props_entity_2:
                secho(f"    No match found!", fg="green")
            print()

    return [suggest for suggest in list(set(suggests_list)) if len(suggest.split()) <= 2]


def get_score_between_two_entitites(entity1: str, entity2: str, model: SentenceEmbedding = None, data_collector: DataCollector = None, freq: Frequencies = None) -> float:
    model = SentenceEmbedding()
    data_collector = DataCollector()
    json_folder = root / 'backend' / 'frequency' /  'jsons' / 'merged' / '20%'
    json_basename = 'ci.json' if 'CI' in os.environ else 'all_1m_filter_3_sort.json'
    freq = Frequencies(json_folder / json_basename, threshold=mapping.FREQUENCY_THRESHOLD)
        
    props1 = data_collector.get_entitiy_props(entity1)
    props2 = data_collector.get_entitiy_props(entity2)
    if not props1 or not props2:
        return 0

    similatiry_edges = utils.get_maximum_weighted_match(model, props1, props2, freq=freq)
    similatiry_edges = sorted(similatiry_edges, key=lambda x: x[2], reverse=True)
    similatiry_edges = similatiry_edges[:3]
    return round(sum([val[2] for val in similatiry_edges]) / len(similatiry_edges), 3)


def get_best_matches_for_entity(entity: str, entities: List[str], n_best: int = 5, verbose: bool = False) -> List[str]:
    best = [(entity, e, get_score_between_two_entitites(e, entity)) for e in entities]
    best = sorted(best, key=lambda x: x[2], reverse=True)
    if verbose:
        for val in best:
            spaces = len(val[0]) + len(val[1])
            secho(f"({val[0]}, {val[1]})", fg="blue", nl=False)
            secho(f"{' '.join([]*(60-spaces))} {val[2]}", fg="blue", bold=True)
    return best[:n_best]


if __name__ == '__main__':
    res = get_best_matches_for_entity("newton", ["faraday", "sky", "window", "paper", "photo", "apple", "tomato", "wall", "home", "horse"])
    print(res)