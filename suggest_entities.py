import json
from typing import List, Dict

from click import secho

import utils
import concept_net
import google_autosuggest
from quasimodo import Quasimodo
from sentence_embadding import SentenceEmbedding

class Suggestions(object):
    def __init__(self, entity: str, prop: str, save_db: bool = True, override_database: bool = False):
        self.entity = entity
        self.prop = prop
        self.override_database = override_database
        self.save_db = save_db
        self.google_suggestinos = utils.read_json('database/google_suggestinos.json') if save_db else {}
    

    def get_suggestions(self):
        should_save = False
        if f"{self.entity}#{self.prop}" in self.google_suggestinos and not self.override_database:
            google_suggestinos = self.google_suggestinos[f"{self.entity}#{self.prop}"]
        else:
            google_suggestinos = google_autosuggest.get_entity_suggestions(self.entity, self.prop)
            self.google_suggestinos[f"{self.entity}#{self.prop}"] = google_suggestinos  
            should_save = True

        if should_save:
            self.save_database()

        return list(set(google_suggestinos))


    def save_database(self):
        with open('database/google_suggestinos.json', 'w') as f1:
            json.dump(self.google_suggestinos, f1, indent='\t')


def get_suggestions_for_missing_entities(model: SentenceEmbedding, base_not_mapped_entities: List[str], base_already_mapping: List[str], target_already_mapping: List[str], verbose: bool = False) -> Dict[str, Dict[str, Dict[str, Dict[str, List[str]]]]]:
    sugges = {}

    # now we iterate on each entity that not mapped (in the same domain), and try to guess to which entity they should be mapped.
    for base_not_mapped_entity in base_not_mapped_entities:
        suggests_list = []
        sugges[base_not_mapped_entity] = {}
        # we need all the relations between the entity (the one that not mapped) to the entities that already mapped (again - in the same domain)
        for idx, base_entity in enumerate(base_already_mapping):
            if verbose: secho(f"{(base_not_mapped_entity, base_entity)}", fg="blue", bold=True)
            sugges[base_not_mapped_entity][base_entity] = {}
            props_entity_1 = model.get_edge_props(base_entity, base_not_mapped_entity)
            props_entity_2 = model.get_edge_props(base_not_mapped_entity, base_entity)

            # we we use the map that we already know (base_entity->target_already_mapping[idx])
            if verbose: secho(f"  {target_already_mapping[idx]}", fg="red", bold=True)
            sugges[base_not_mapped_entity][base_entity][target_already_mapping[idx]] = {}
            for prop in (props_entity_1 + props_entity_2):
                suggestions_model = Suggestions(target_already_mapping[idx], prop)
                props = suggestions_model.get_suggestions()
                if props:
                    # we found candidates for '<exist_entity> <prop> <candidate>' or '<candidate> <prop> <exist_entity>'
                    sugges[base_not_mapped_entity][base_entity][target_already_mapping[idx]][prop] = props
                    suggests_list.extend(props)
                    if verbose:
                        secho(f"    {prop}: ", fg="green", bold=True, nl=False)
                        secho(f"{props}", fg="cyan")
            if verbose: 
                if not props_entity_1 + props_entity_2:
                    secho(f"    No match found!", fg="green")
                print()

        sugges[base_not_mapped_entity] = get_best_matches_for_entity(base_not_mapped_entity, list(set(suggests_list)), n_best=5, verbose=True, model=model, quasimodo=model.quasimodo)
    return sugges


def get_entitiy_props(entity: str, quasimodo: Quasimodo = None) -> List[str]:
    if not quasimodo: quasimodo = Quasimodo()

    quasimodo_db = utils.read_json('database/quasimodo_nodes.json')
    if entity not in quasimodo_db:
        quasimodo_db[entity] = [[prop[0], prop[1]] for prop in quasimodo.get_entity_props(entity, n_largest=5)]
        with open('database/quasimodo_nodes.json', 'w') as f1:
            json.dump(quasimodo_db, f1, indent='\t')

    quasimodo_props = [f"{prop[0]} {prop[1]}" for prop in quasimodo_db[entity]]
    concept_net_props = concept_net.get_entity_props(entity, quasimodo.engine)
    google_props = google_autosuggest.get_entity_props(entity)
    return list(set(quasimodo_props + concept_net_props + google_props))


def get_score_between_two_entitites(entity1: str, entity2: str, model: SentenceEmbedding = None, quasimodo: Quasimodo = None) -> float:
    if not quasimodo: quasimodo = Quasimodo()
    if not model: model = SentenceEmbedding()
    props1 = get_entitiy_props(entity1, quasimodo)
    props2 = get_entitiy_props(entity2, quasimodo)
    if not props1 or not props2:
        return 0

    similatiry_edges = utils.get_maximum_weighted_match(model, props1, props2)
    similatiry_edges = sorted(similatiry_edges, key=lambda x: x[2], reverse=True)
    similatiry_edges = similatiry_edges[:3]
    return round(sum([val[2] for val in similatiry_edges]) / len(similatiry_edges), 3)


def get_best_matches_for_entity(entity: str, entities: List[str], n_best: int = 5, verbose: bool = False, model: SentenceEmbedding = None, quasimodo: Quasimodo = None) -> List[str]:
    best = [(entity, e, get_score_between_two_entitites(e, entity, model, quasimodo)) for e in entities]
    best = sorted(best, key=lambda x: x[2], reverse=True)
    if verbose:
        for val in best:
            spaces = len(val[0]) + len(val[1])
            secho(f"({val[0]}, {val[1]})", fg="blue", nl=False)
            secho(f"{' '.join([]*(60-spaces))} {val[2]}", fg="blue", bold=True)
    return best[:n_best]


if __name__ == '__main__':
    # get_score_between_two_entitites("newton", "faraday")
    pass