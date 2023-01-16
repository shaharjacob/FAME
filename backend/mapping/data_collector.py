import os
import json
import inflect
from pathlib import Path
from typing import List, Optional, Dict, Set

from . import openIE
from . import concept_net
from . import google_autosuggest
from . import gpt3
from .quasimodo import Quasimodo

root = Path(__file__).resolve().parent.parent.parent

class DataCollector(object):
    def __init__(self, api: dict, quasimodo: Optional[Quasimodo] = None):

        self.quasimodo = quasimodo
        self.engine = None
        self.api = api
        if api.get("google", False):
            self.google_edges = read_json(root / 'backend' / 'database' / 'google_edges.json')
        if api.get("openie", False):
            self.openie = read_json(root / 'backend' / 'database' / 'openie_edges.json')
        if api.get("quasimodo", False):
            self.quasimodo_edges = read_json(root / 'backend' / 'database' / 'quasimodo_edges.json')
        if api.get("conceptnet", False):
            self.conceptnet_edges = read_json(root / 'backend' / 'database' / 'conceptnet_edges.json')
        # if api.get("gpt3", False):
        #     self.gpt3_edges = read_json(root / 'backend' / 'database' / 'gpt3_edges.json')

        self.stopwords = read_stopwords(root / 'backend' / 'frequency' / 'stopwords.txt')


    def get_entities_relations(self, entity1: str, entity2: str, from_where: bool = False) -> List[str]:
        if self.api.get("google", False):
            if f"{entity1}#{entity2}" in self.google_edges:
                autosuggets_props = self.google_edges[f"{entity1}#{entity2}"]
            else:
                autosuggets_props = google_autosuggest.get_entities_relations(entity1, entity2).get("props", [])
                self.google_edges[f"{entity1}#{entity2}"] = sorted(autosuggets_props) 
                with open(root / 'backend' / 'database' / 'google_edges.json', 'w') as f2:
                    json.dump(self.google_edges, f2, indent='\t')
        else:
            autosuggets_props = []

        if self.api.get("openie", False):
            if f"{entity1}#{entity2}" in self.openie:
                openie_props = self.openie[f"{entity1}#{entity2}"]
            else:
                openie_props = []
                # # You should download the database from here: https://allenai.org/data/openie-demo
                # # Then you should split it to tsv files, two depth-directroies for the first two letters of the subjects.
                # # full support will be in the future.
                # openie_props = openIE.entities_relations_wrapper(entity1, entity2, n=10)
                # self.openie[f"{entity1}#{entity2}"] = sorted(openie_props)
                # with open(root / 'backend' / 'database' / 'openie_edges.json', 'w') as f4:
                #     json.dump(self.openie, f4, indent='\t')
        else:
            openie_props = []

        if self.api.get("quasimodo", False):
            if f"{entity1}#{entity2}" in self.quasimodo_edges:
                quasimodo_props = self.quasimodo_edges[f"{entity1}#{entity2}"]
            else:
                if not self.quasimodo:
                    self.quasimodo = Quasimodo(path=root / 'backend' / 'tsv' / 'merged' / 'quasimodo.tsv')
                quasimodo_props = self.quasimodo.get_entities_relations(entity1, entity2, n_largest=10, plural_and_singular=True)
                self.quasimodo_edges[f"{entity1}#{entity2}"] = sorted(quasimodo_props)
                with open(root / 'backend' / 'database' / 'quasimodo_edges.json', 'w') as f1:
                    json.dump(self.quasimodo_edges, f1, indent='\t')
        else:
            quasimodo_props = []

        if self.api.get("conceptnet", False):
            if f"{entity1}#{entity2}" in self.conceptnet_edges:
                concept_net_props = self.conceptnet_edges[f"{entity1}#{entity2}"]
            else:
                if not self.engine:
                    self.engine = inflect.engine()
                concept_net_props = concept_net.get_entities_relations(entity1, entity2, self.engine, plural_and_singular=True)
                self.conceptnet_edges[f"{entity1}#{entity2}"] = sorted(concept_net_props)
                with open(root / 'backend' / 'database' / 'conceptnet_edges.json', 'w') as f3:
                    json.dump(self.conceptnet_edges, f3, indent='\t')
        else:
            concept_net_props = []
        
        if self.api.get("gpt3", False):
            if not self.engine:
                self.engine = inflect.engine()
            gpt3_props = gpt3.get_entities_relations(entity1, entity2, self.engine)
        else:
            gpt3_props = []

        quasimodo_props = [prop for prop in quasimodo_props if prop not in self.stopwords]
        autosuggets_props = [prop for prop in autosuggets_props if prop not in self.stopwords]
        concept_net_props = [prop for prop in concept_net_props if prop not in self.stopwords]
        openie_props = [prop for prop in openie_props if prop not in self.stopwords]
        gpt3_props = [prop for prop in gpt3_props if prop not in self.stopwords]

        if from_where:
            return {
                "openie": sorted(list(set(openie_props))),
                "quasimodo": sorted(list(set(quasimodo_props))),
                "concept_net": sorted(list(set(concept_net_props))),
                "google_autosuggest": sorted(list(set(autosuggets_props))),
                "gpt3": sorted(list(set(gpt3_props))),
            }

        return sorted(list(set(quasimodo_props + autosuggets_props + concept_net_props + openie_props + gpt3_props)))
    

    # def get_entitiy_props(self, entity: str, from_where: bool = False) -> List[str]:
    #     if self.api.get("quasimodo", False):
    #         quasimodo_db = read_json(root / 'backend' / 'database' / 'quasimodo_nodes.json')
    #         if entity not in quasimodo_db:
    #             if not self.quasimodo:
    #                 self.quasimodo = Quasimodo(path=root / 'backend' / 'tsv' / 'merged' / 'quasimodo.tsv')
    #             quasimodo_db[entity] = sorted([[prop[0], prop[1]] for prop in self.quasimodo.get_entity_props(entity, n_largest=5)])
    #             with open(root / 'backend' / 'database' / 'quasimodo_nodes.json', 'w') as f1:
    #                 json.dump(quasimodo_db, f1, indent='\t')
    #         quasimodo_props = [f"{prop[0]} {prop[1]}" for prop in quasimodo_db[entity]]
    #     else:
    #         quasimodo_props = []
        
    #     if self.api.get("conceptnet", False):
    #         concept_net_props = concept_net.get_entity_props(entity)
    #     else:
    #         concept_net_props = []
            
    #     if self.api.get("google", False):
    #         google_props = google_autosuggest.get_entity_props(entity)
    #     else:
    #         google_props = []

    #     if from_where:
    #         return {
    #             "quasimodo": sorted(list(set(quasimodo_props))),
    #             "concept_net": sorted(list(set(concept_net_props))),
    #             "google_autosuggest": sorted(list(set(google_props))),
    #         }

    #     return sorted(list(set(quasimodo_props + concept_net_props + google_props)))


def read_json(path: str) -> Dict[str, List[str]]:
    with open(path, 'r') as f:
        return json.load(f)
    

def read_stopwords(path: str) -> Set[str]:
    with open(path, 'r') as f:
        return set([word.strip() for word in f.read().split('\n')])


if __name__ == '__main__':
    api = {
        "google": True,
        "openie": True,
        "quasimodo": True,
        "gpt3": True,
        "conceptnet": False
    }
    data_collector = DataCollector(api=api)
    # res = data_collector.get_entities_relations("sun", "summer")
    res = data_collector.get_entities_relations("rain", "winter")
    print(res)