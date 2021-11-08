import os
import json
import inflect
from pathlib import Path
from typing import List, Optional, Dict, Set

from sqlitedict import SqliteDict

from . import openIE
from . import concept_net
from . import google_autosuggest
from .quasimodo import Quasimodo

root = Path(__file__).resolve().parent.parent.parent

class DBRelations(object):
    def __init__(self):
        self.conceptnet_relations = SqliteDict(
                    root / 'backend' / 'database' / 'conceptnet_relations.sqlite',
                    encode=json.dumps,
                    decode=json.loads
                )
        self.google_relations = SqliteDict(
                    root / 'backend' / 'database' / 'google_relations.sqlite',
                    encode=json.dumps,
                    decode=json.loads
                )
        self.quasimodo_relations = SqliteDict(
                    root / 'backend' / 'database' / 'quasimodo_relations.sqlite',
                    encode=json.dumps,
                    decode=json.loads
                )
        self.openie_relations = SqliteDict(
                    root / 'backend' / 'database' / 'openie_relations.sqlite',
                    encode=json.dumps,
                    decode=json.loads
                )
        self.should_commit = {
            "conceptnet_relations": False,
            "google_relations": False,
            "quasimodo_relations": False,
            "openie_relations": False
        }

    def commit(self):
        if self.should_commit["conceptnet_relations"]:
            self.conceptnet_relations.commit()
        if self.should_commit["google_relations"]:
            self.google_relations.commit()
        if self.should_commit["quasimodo_relations"]:
            self.quasimodo_relations.commit()
        if self.should_commit["openie_relations"]:
            self.openie_relations.commit()
    
    def close(self):
        self.conceptnet_relations.close()
        self.google_relations.close()
        self.quasimodo_relations.close()
        self.openie_relations.close()

class DataCollector(object):
    def __init__(self, quasimodo: Optional[Quasimodo] = None, engine: Optional[inflect.engine] = None):
        self.quasimodo = quasimodo
        self.engine = engine
        self.db = DBRelations()
        self.stopwords = read_stopwords(root / 'backend' / 'frequency' / 'stopwords.txt')


    def get_entities_relations(self, entity1: str, entity2: str, from_where: bool = False) -> List[str]:
        if f"{entity1}#{entity2}" in self.db.quasimodo_relations:
            quasimodo_relations = self.db.quasimodo_relations[f"{entity1}#{entity2}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path=root / 'backend' / 'tsv' / 'merged' / 'quasimodo.tsv')
            quasimodo_relations = self.quasimodo.get_entities_relations(entity1, entity2, n_largest=10, plural_and_singular=True)
            self.db.quasimodo_relations[f"{entity1}#{entity2}"] = sorted(quasimodo_relations)
            self.db.should_commit["quasimodo_relations"] = True
        
        if 'SKIP_GOOGLE' not in os.environ:
            if f"{entity1}#{entity2}" in self.db.google_relations:
                google_relations = self.db.google_relations[f"{entity1}#{entity2}"]
            else:
                google_relations = google_autosuggest.get_entities_relations(entity1, entity2).get("props", [])
                self.db.google_relations[f"{entity1}#{entity2}"] = sorted(google_relations) 
                self.db.should_commit["google_relations"] = True
        else:
            google_relations = []
        
        if f"{entity1}#{entity2}" in self.db.openie_relations:
            openie_relations = self.db.openie_relations[f"{entity1}#{entity2}"]
        else:
            openie_relations = openIE.entities_relations_wrapper(entity1, entity2, n=0)
            self.db.openie_relations[f"{entity1}#{entity2}"] = sorted(openie_relations)
            self.db.should_commit["openie_relations"] = True
            
        # if f"{entity1}#{entity2}" in self.db.conceptnet_relations:
        #     conceptnet_relations = self.db.conceptnet_relations[f"{entity1}#{entity2}"]
        # else:
        #     if not self.engine:
        #         self.engine = inflect.engine()
        #     conceptnet_relations = concept_net.get_entities_relations(entity1, entity2, self.engine, plural_and_singular=True)
        #     self.db.conceptnet_relations[f"{entity1}#{entity2}"] = sorted(conceptnet_relations)
        #     self.db.should_commit["conceptnet_relations"] = True

        self.db.commit()
        
        quasimodo_relations = [prop for prop in quasimodo_relations if prop not in self.stopwords]
        google_relations = [prop for prop in google_relations if prop not in self.stopwords]
        # conceptnet_relations = [prop for prop in conceptnet_relations if prop not in self.stopwords]
        openie_relations = [prop for prop in openie_relations if prop not in self.stopwords]

        if from_where:
            return {
                "openie": sorted(list(set(openie_relations))),
                "quasimodo": sorted(list(set(quasimodo_relations))),
                # "concept_net": sorted(list(set(conceptnet_relations))),
                "google_autosuggest": sorted(list(set(google_relations))),
            }

        # return sorted(list(set(quasimodo_relations + google_relations + conceptnet_relations + openie_relations)))
        return sorted(list(set(quasimodo_relations + google_relations + openie_relations)))
    

    def get_entitiy_props(self, entity: str, from_where: bool = False) -> List[str]:
        quasimodo_db = read_json(root / 'backend' / 'database' / 'quasimodo_nodes.json')
        if entity not in quasimodo_db:
            if not self.quasimodo:
                self.quasimodo = Quasimodo(path=root / 'backend' / 'tsv' / 'merged' / 'quasimodo.tsv')
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