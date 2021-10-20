import json
import inflect
from pathlib import Path
from typing import List, Optional, Dict, Set

from . import openIE
from . import concept_net
from . import google_autosuggest
from .quasimodo import Quasimodo

root = Path(__file__).resolve().parent.parent.parent

class DataCollector(object):
    def __init__(self, quasimodo: Optional[Quasimodo] = None, engine: Optional[inflect.engine] = None, save_database: bool = True, override_database: bool = False):
        self.quasimodo = quasimodo
        self.engine = engine
        self.override_database = override_database
        self.save_database = save_database
        self.quasimodo_edges = read_json(root / 'backend' / 'database' / 'quasimodo_edges.json') if save_database else {}
        self.google_edges = read_json(root / 'backend' / 'database' / 'google_edges.json') if save_database else {}
        self.conceptnet_edges = read_json(root / 'backend' / 'database' / 'conceptnet_edges.json') if save_database else {}
        self.openie = read_json(root / 'backend' / 'database' / 'openie_edges.json') if save_database else {}
        self.stopwords = read_stopwords(root / 'backend' / 'frequency' / 'stopwords.txt')


    def get_entities_relations(self, entity1: str, entity2: str, from_where: bool = False) -> List[str]:
        should_save = False
        if f"{entity1}#{entity2}" in self.quasimodo_edges and not self.override_database:
            quasimodo_props = self.quasimodo_edges[f"{entity1}#{entity2}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path=root / 'tsv' / 'quasimodo.tsv')
            quasimodo_props = self.quasimodo.get_entities_relations(entity1, entity2, n_largest=10, plural_and_singular=True)
            self.quasimodo_edges[f"{entity1}#{entity2}"] = sorted(quasimodo_props)
            should_save = True

        if f"{entity1}#{entity2}" in self.google_edges and not self.override_database:
            autosuggets_props = self.google_edges[f"{entity1}#{entity2}"]
        else:
            autosuggets_props = google_autosuggest.get_entities_relations(entity1, entity2).get("props", [])
            self.google_edges[f"{entity1}#{entity2}"] = sorted(autosuggets_props) 
            should_save = True

        # if f"{entity1}#{entity2}" in self.conceptnet_edges and not self.override_database:
        #     concept_net_props = self.conceptnet_edges[f"{entity1}#{entity2}"]
        # else:
        #     if not self.engine:
        #         self.engine = inflect.engine()
        #     concept_net_props = concept_net.get_entities_relations(entity1, entity2, self.engine, plural_and_singular=True)
        #     self.conceptnet_edges[f"{entity1}#{entity2}"] = sorted(concept_net_props)
        #     should_save = True

        if f"{entity1}#{entity2}" in self.openie and not self.override_database:
            openie_props = self.openie[f"{entity1}#{entity2}"]
        else:
            openie_props = openIE.entities_relations_wrapper(entity1, entity2, n=0)
            self.openie[f"{entity1}#{entity2}"] = sorted(openie_props)
            should_save = True
            
        if should_save:
            self.save_database_()
        
        quasimodo_props = [prop for prop in quasimodo_props if prop not in self.stopwords]
        autosuggets_props = [prop for prop in autosuggets_props if prop not in self.stopwords]
        # concept_net_props = [prop for prop in concept_net_props if prop not in self.stopwords]
        openie_props = [prop for prop in openie_props if prop not in self.stopwords]

        if from_where:
            return {
                "openie": sorted(list(set(openie_props))),
                "quasimodo": sorted(list(set(quasimodo_props))),
                # "concept_net": sorted(list(set(concept_net_props))),
                "google_autosuggest": sorted(list(set(autosuggets_props))),
            }

        # return sorted(list(set(quasimodo_props + autosuggets_props + concept_net_props + openie_props)))
        return sorted(list(set(quasimodo_props + autosuggets_props + openie_props)))
    

    def get_entitiy_props(self, entity: str, from_where: bool = False) -> List[str]:
        quasimodo_db = read_json(root / 'backend' / 'database' / 'quasimodo_nodes.json')
        if entity not in quasimodo_db:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path=root / 'tsv' / 'quasimodo.tsv')
            quasimodo_db[entity] = sorted([[prop[0], prop[1]] for prop in self.quasimodo.get_entity_props(entity, n_largest=5)])
            with open(root / 'backend' / 'database' / 'quasimodo_nodes.json', 'w') as f1:
                json.dump(quasimodo_db, f1, indent='\t')

        quasimodo_props = [f"{prop[0]} {prop[1]}" for prop in quasimodo_db[entity]]
        concept_net_props = concept_net.get_entity_props(entity)
        google_props = google_autosuggest.get_entity_props(entity)

        if from_where:
            return {
                "quasimodo": sorted(list(set(quasimodo_props))),
                "concept_net": sorted(list(set(concept_net_props))),
                "google_autosuggest": sorted(list(set(google_props))),
            }

        return sorted(list(set(quasimodo_props + concept_net_props + google_props)))


    def save_database_(self):
        with open(root / 'backend' / 'database' / 'quasimodo_edges.json', 'w') as f1:
            json.dump(self.quasimodo_edges, f1, indent='\t')
        with open(root / 'backend' / 'database' / 'google_edges.json', 'w') as f2:
            json.dump(self.google_edges, f2, indent='\t')
        with open(root / 'backend' / 'database' / 'conceptnet_edges.json', 'w') as f3:
            json.dump(self.conceptnet_edges, f3, indent='\t')
        with open(root / 'backend' / 'database' / 'openie_edges.json', 'w') as f3:
            json.dump(self.openie, f3, indent='\t')


def read_json(path: str) -> Dict[str, List[str]]:
    with open(path, 'r') as f:
        return json.load(f)
    

def read_stopwords(path: str) -> Set[str]:
    with open(path, 'r') as f:
        return set([word.strip() for word in f.read().split('\n')])


if __name__ == '__main__':
    data_collector = DataCollector()
    # res = data_collector.get_entities_relations("sun", "summer")
    res = data_collector.get_entities_relations("rain", "winter")
    print(res)