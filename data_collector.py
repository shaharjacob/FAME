import json
from typing import List

import utils
import inflect
import concept_net
import google_autosuggest
from quasimodo import Quasimodo

class DataCollector(object):
    def __init__(self, init_quasimodo: bool = False, init_inflect: bool = False, save_database: bool = True, override_database: bool = False):
        self.quasimodo = None
        if init_quasimodo:
            self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
        self.engine = None
        if init_inflect:
            self.engine = inflect.engine()
        self.override_database = override_database
        self.save_database = save_database
        self.quasimodo_edges = utils.read_json('database/quasimodo_edges.json') if save_database else {}
        self.google_edges = utils.read_json('database/google_edges.json') if save_database else {}
        self.conceptnet_edges = utils.read_json('database/conceptnet_edges.json') if save_database else {}


    def get_entities_relations(self, entity1: str, entity2: str) -> List[str]:
        should_save = False
        if f"{entity1}#{entity2}" in self.quasimodo_edges and not self.override_database:
            quasimodo_props = self.quasimodo_edges[f"{entity1}#{entity2}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
            quasimodo_props = self.quasimodo.get_entities_relations(entity1, entity2, n_largest=10, plural_and_singular=True)
            self.quasimodo_edges[f"{entity1}#{entity2}"] = sorted(quasimodo_props)
            should_save = True

        if f"{entity1}#{entity2}" in self.google_edges and not self.override_database:
            autocomplete_props = self.google_edges[f"{entity1}#{entity2}"]
        else:
            autocomplete_props = google_autosuggest.get_entities_relations(entity1, entity2).get("props", [])
            self.google_edges[f"{entity1}#{entity2}"] = sorted(autocomplete_props) 
            should_save = True

        if f"{entity1}#{entity2}" in self.conceptnet_edges and not self.override_database:
            concept_new_props = self.conceptnet_edges[f"{entity1}#{entity2}"]
        else:
            if not self.engine:
                self.engine = inflect.engine()
            concept_new_props = concept_net.get_entities_relations(entity1, entity2, self.engine, plural_and_singular=True)
            self.conceptnet_edges[f"{entity1}#{entity2}"] = sorted(concept_new_props)
            should_save = True

        if should_save:
            self.save_database_()
        
        properties = set(quasimodo_props + autocomplete_props + concept_new_props)
        properties.discard("has property")
        return list(properties)
    

    def get_entitiy_props(self, entity: str) -> List[str]:
        quasimodo_db = utils.read_json('database/quasimodo_nodes.json')
        if entity not in quasimodo_db:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path='tsv/quasimodo.tsv')
            quasimodo_db[entity] = sorted([[prop[0], prop[1]] for prop in self.quasimodo.get_entity_props(entity, n_largest=5)])
            with open('database/quasimodo_nodes.json', 'w') as f1:
                json.dump(quasimodo_db, f1, indent='\t')

        quasimodo_props = [f"{prop[0]} {prop[1]}" for prop in quasimodo_db[entity]]
        concept_net_props = concept_net.get_entity_props(entity)
        google_props = google_autosuggest.get_entity_props(entity)
        return list(set(quasimodo_props + concept_net_props + google_props))


    def save_database_(self):
        with open('database/quasimodo_edges.json', 'w') as f1:
            json.dump(self.quasimodo_edges, f1, indent='\t')
        with open('database/google_edges.json', 'w') as f2:
            json.dump(self.google_edges, f2, indent='\t')
        with open('database/conceptnet_edges.json', 'w') as f3:
            json.dump(self.conceptnet_edges, f3, indent='\t')