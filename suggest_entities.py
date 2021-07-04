import json
from typing import List, Tuple, Dict

from click import secho

import utils
import google_autosuggest
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


def get_suggestions_for_missing_base_entities(model: SentenceEmbedding, 
                                            base: List[str], 
                                            base_already_mapping: List[str], 
                                            target_already_mapping: List[str],
                                            verbose: bool = False):
    sugges = {}

    # first we need to extract the entities that not mapped
    base_not_mapped_entities = [entity for entity in base if entity not in base_already_mapping]

    # now we iterate on each iterate that not mapped (in the same domain), and try to guess to which entity they should be mapped.
    for base_not_mapped_entity in base_not_mapped_entities:

        # we need all the relations between the entity (the one that not mapped) to the entities that already mapped (again - in the same domain)
        for base_entity in base_already_mapping:
            if verbose: secho(f"{(base_not_mapped_entity, base_entity)}", fg="blue", bold=True)
            sugges[(base_not_mapped_entity, base_entity)] = {}
            props_entity_1 = model.get_edge_props(base_entity, base_not_mapped_entity)
            props_entity_2 = model.get_edge_props(base_not_mapped_entity, base_entity)

            # after we have all the relations, we need to iterate over the second domain, and looking for possible entitites, based on these relations.
            for target_entity in target_already_mapping:
                if verbose: secho(f"  {target_entity}", fg="red", bold=True)
                sugges[(base_not_mapped_entity, base_entity)][target_entity] = {}
                for prop in (props_entity_1 + props_entity_2):
                    suggestions_model = Suggestions(target_entity, prop)
                    props = suggestions_model.get_suggestions()
                    if props:
                        # we found candidates for '<exist_entity> <prop> <candidate>' or '<candidate> <prop> <exist_entity>'
                        sugges[(base_not_mapped_entity, base_entity)][target_entity][prop] = props
                        if verbose:
                            secho(f"    {prop}: ", fg="green", bold=True, nl=False)
                            secho(f"{props}", fg="cyan")
                if verbose: 
                    if not props_entity_1 + props_entity_2:
                        secho(f"    No match found!: ", fg="green")
                    print()
            if verbose: print()
