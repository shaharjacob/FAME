import os
import json
import copy
from pathlib import Path
from typing import List, Tuple, Set, Dict

from click import secho

from . import openIE
from utils import utils
from . import google_autosuggest
from .quasimodo import Quasimodo
from .data_collector import DataCollector
from frequency.frequency import Frequencies
from utils.sentence_embadding import SentenceEmbedding
from .mapping import Solution, Pair, SingleMatch, FREQUENCY_THRESHOLD
from .mapping import get_score, update_already_mapping, update_paris_map, get_all_possible_pairs_map, get_best_pair_mapping

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
        if f"{self.entity}#{self.prop}" in self.quasimodo_suggestinos and not self.override_database:
            quasimodo_suggestinos = self.quasimodo_suggestinos[f"{self.entity}#{self.prop}"]
        else:
            if not self.quasimodo:
                self.quasimodo = Quasimodo()
            quasimodo_suggestinos = self.quasimodo.get_entity_suggestions(self.entity, self.prop, n_largest=5, plural_and_singular=True)
            self.quasimodo_suggestinos[f"{self.entity}#{self.prop}"] = quasimodo_suggestinos  
            should_save = True

        if 'SKIP_GOOGLE' not in os.environ:
            if f"{self.entity}#{self.prop}" in self.google_suggestinos and not self.override_database:
                google_suggestinos = self.google_suggestinos[f"{self.entity}#{self.prop}"]
            else:
                google_suggestinos = google_autosuggest.get_entity_suggestions(self.entity, self.prop)
                self.google_suggestinos[f"{self.entity}#{self.prop}"] = google_suggestinos  
                should_save = True
        else:
            google_suggestinos = []

        if 'SKIP_GOOGLE' in os.environ:
            if f"{self.entity}#{self.prop}" in self.openie_suggestinos and not self.override_database:
                openie_suggestinos = self.openie_suggestinos[f"{self.entity}#{self.prop}"]
            else:
                openie_suggestinos = openIE.get_entity_suggestions_wrapper(self.entity, self.prop, n_largest=5)
                self.openie_suggestinos[f"{self.entity}#{self.prop}"] = openie_suggestinos  
                should_save = True
        else:
            openie_suggestinos = []

        if should_save:
            self.save_database()

        suggestions = google_suggestinos + quasimodo_suggestinos + openie_suggestinos
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
                                         model: SentenceEmbedding, 
                                         verbose: bool = False
                                         ) -> List[str]:
    suggests_list = {}
    # we need all the relations between the entity (the one that not mapped) to the entities that already mapped (again - in the same domain)
    for idx, base_entity in enumerate(base_already_mapping):
        match_target_entity = target_already_mapping[idx]
        if verbose: 
            secho(f"(^{base_not_mapped_entity}, {base_entity})", fg="blue", bold=True)

        props_entity_1 = data_collector.get_entities_relations(base_entity, base_not_mapped_entity)
        props_entity_2 = data_collector.get_entities_relations(base_not_mapped_entity, base_entity)

        # we we use the map that we already know (base_entity -> match_target_entity)
        if verbose: 
            secho(f"  {match_target_entity}", fg="red", bold=True)
        actual_props = []
        for prop in set(props_entity_1 + props_entity_2):
            suggestions_model = Suggestions(match_target_entity, prop, quasimodo=data_collector.quasimodo)
            props = suggestions_model.get_suggestions()
            if props:
                # we found candidates for '<exist_entity> <prop> <candidate>' or '<candidate> <prop> <exist_entity>'
                props_filtered = [p for p in props if len(p.split()) <= 2]
                actual_props.extend(props_filtered)
                if verbose:
                    secho(f"    {prop}: ", fg="green", bold=True, nl=False)
                    secho(f"{list(set(props_filtered))}", fg="cyan")
        
        if verbose: 
            if not props_entity_1 + props_entity_2:
                secho(f"    No match found!", fg="green")
            print()
        
        clusters = {v[0]: v for _, v in model.clustering((actual_props), 0.6).items()}
        clusters_filtered = {k: list(set(v)) for k, v in clusters.items() if len(v) > 0}
        suggests_list[match_target_entity] = clusters_filtered
        
    return suggests_list


def get_score_between_two_entitites(entity1: str, entity2: str, model: SentenceEmbedding = None, data_collector: DataCollector = None, freq: Frequencies = None) -> float:
    model = SentenceEmbedding()
    data_collector = DataCollector()
    json_folder = root / 'backend' / 'frequency'
    freq = Frequencies(json_folder / 'freq.json', threshold=FREQUENCY_THRESHOLD)
        
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


def mapping_suggestions_helper(
    available_pairs: List[List[SingleMatch]],
    current_solution: Solution,
    solutions: List[Solution],
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    data_collector: DataCollector,
    model: SentenceEmbedding,
    freq: Frequencies,
    top_suggestions: List[str],
    domain: str,
    cache: dict,
    num_of_suggestions: int = 1):
    """this function is use for mapping in suggestions mode. this is only one iteration"""
    
    # we will get the top-num-of-suggestions with the best score.
    best_results_for_current_iteration = get_best_pair_mapping(model, freq, data_collector, available_pairs, cache, num_of_suggestions)
    for result in best_results_for_current_iteration:
        # if the best score is > 0, we will update the base and target lists of the already mapping entities.
        # otherwise, if the best score is 0, we have no more mappings to do.
        if result["best_score"] > 0:
            # we will add the new mapping to the already mapping lists. 
            base_already_mapping_new = copy.deepcopy(current_solution.actual_base)
            target_already_mapping_new = copy.deepcopy(current_solution.actual_target)
            actual_mapping_indecies_new = copy.deepcopy(current_solution.actual_indecies)
            b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
            t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
            
            score = 0
            if b1 not in base_already_mapping_new and t1 not in target_already_mapping_new:
                score += result["best_score"]
                # score += get_score(base_already_mapping_new, target_already_mapping_new, b1, t1, cache)
                update_already_mapping(b1, t1, base_already_mapping_new, target_already_mapping_new, actual_mapping_indecies_new)
            
            if b2 not in base_already_mapping_new and t2 not in target_already_mapping_new:
                score += result["best_score"]
                # score += get_score(base_already_mapping_new, target_already_mapping_new, b2, t2, cache)
                update_already_mapping(b2, t2, base_already_mapping_new, target_already_mapping_new, actual_mapping_indecies_new)
            
            mapping_repr = [f"{b} --> {t}" for b, t in zip(base_already_mapping_new, target_already_mapping_new)]
            mapping_repr_as_tuple = tuple(sorted(mapping_repr))
            if mapping_repr_as_tuple in mappings_already_seen:
                continue
            mappings_already_seen.add(mapping_repr_as_tuple)
            
            # sometimes it found the same entity
            if target_already_mapping_new[-1] == base_already_mapping_new[-1]:
                continue
            
            # we need to add the mapping that we just found to the relations that already exist for that solution.
            relations = copy.deepcopy(current_solution.relations)
            relations.append(result["best_mapping"])
            scores_copy = copy.deepcopy(current_solution.scores)
            scores_copy.append(round(result["best_score"], 3))
            coverage = copy.deepcopy(current_solution.coverage)
            coverage.append(result["coverage"])
            
            relations_as_tuple = tuple([tuple(relation) for relation in sorted(relations)])
            if relations_as_tuple in relations_already_seen:
                continue
            relations_already_seen.add(relations_as_tuple)
                
            # updating the top suggestions for the GUI
            if domain == "actual_base":
                top_suggestions.append(target_already_mapping_new[-1])
            elif domain == "actual_target":
                top_suggestions.append(base_already_mapping_new[-1])
                
            solutions.append(Solution(
                mapping=[f"{b} --> {t}" for b, t in zip(base_already_mapping_new, target_already_mapping_new)],
                relations=relations,
                scores=scores_copy,
                score=round(current_solution.score + score, 3),
                actual_base=base_already_mapping_new,
                actual_target=target_already_mapping_new,
                actual_indecies=actual_mapping_indecies_new,
                length=len(base_already_mapping_new),
                coverage=coverage,
            ))


def mapping_suggestions(
    domain: List[str],
    first_domain: str, 
    second_domain: str, 
    solution: Solution, 
    data_collector: DataCollector,
    model: SentenceEmbedding, 
    freq: Frequencies,
    solutions: List[Solution],
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    cache: dict,
    num_of_suggestions: int = 1,
    verbose: bool = False):
    
    first_domain_not_mapped_entities = [entity for entity in domain if entity not in solution.get_actual(first_domain)]
    for first_domain_not_mapped_entity in first_domain_not_mapped_entities:
        # we will go over and entities from the first domain and extract the relations with 'first_domain_not_mapped_entity'
        # then, we will store in a dict in the key the corresponding entity from the second domain, and in the value the relations.
        entities_suggestions: Dict[str, List[str]] = get_suggestions_for_missing_entities(  data_collector, 
                                                                                            first_domain_not_mapped_entity, 
                                                                                            solution.get_actual(first_domain), 
                                                                                            solution.get_actual(second_domain), 
                                                                                            model=model,
                                                                                            verbose=verbose)
        for key, value in entities_suggestions.items():
            clusters_representors = list(value.keys())
            if not clusters_representors:
                continue  # no suggestion found :(
            
            if first_domain == "actual_base":
                new_base = solution.get_actual("actual_base") + [first_domain_not_mapped_entity]
                new_target = solution.get_actual("actual_target") + clusters_representors
                index_domain = 1
                
            else: # first_domain == "actual_target"
                new_base = solution.get_actual("actual_base") + clusters_representors
                new_target = solution.get_actual("actual_target") + [first_domain_not_mapped_entity]
                index_domain = 0
                
            all_pairs = get_all_possible_pairs_map(new_base, new_target)
            available_pairs_new = update_paris_map(all_pairs, solution.get_actual("actual_base"), solution.get_actual("actual_target"), solution.actual_indecies)
            
            pair_allows: Set[Tuple[str, str]] = set([(key, v) for v in clusters_representors])
            available_pairs_new = [pair for pair in available_pairs_new if pair[0][index_domain] in pair_allows]
            if not available_pairs_new:
                continue
            
            top_suggestions = []
            mapping_suggestions_helper(
                available_pairs=available_pairs_new,
                current_solution=copy.deepcopy(solution),
                solutions=solutions,
                relations_already_seen=relations_already_seen,
                mappings_already_seen=mappings_already_seen,
                data_collector=data_collector,
                model=model,
                freq=freq,
                top_suggestions=top_suggestions,
                domain=first_domain,
                cache=cache,
                num_of_suggestions=num_of_suggestions,
            )
            
            if top_suggestions:
                best_cluster_representor = top_suggestions[0]
                best_cluster_suggestions = value[best_cluster_representor]
                best_cluster_suggestions.remove(best_cluster_representor)
                if best_cluster_suggestions:
                    if first_domain == "actual_base":
                        new_base = solution.get_actual("actual_base") + [first_domain_not_mapped_entity]
                        new_target = solution.get_actual("actual_target") + best_cluster_suggestions
                        index_domain = 1
                        
                    else: # first_domain == "actual_target"
                        new_base = solution.get_actual("actual_base") + best_cluster_suggestions
                        new_target = solution.get_actual("actual_target") + [first_domain_not_mapped_entity]
                        index_domain = 0
                        
                    all_pairs = get_all_possible_pairs_map(new_base, new_target)
                    available_pairs_new = update_paris_map(all_pairs, solution.get_actual("actual_base"), solution.get_actual("actual_target"), solution.actual_indecies)
                    
                    pair_allows: Set[Tuple[str, str]] = set([(key, v) for v in best_cluster_suggestions])
                    available_pairs_new = [pair for pair in available_pairs_new if pair[0][index_domain] in pair_allows]
                    if available_pairs_new:
                        mapping_suggestions_helper(
                            available_pairs=available_pairs_new,
                            current_solution=copy.deepcopy(solution),
                            solutions=solutions,
                            relations_already_seen=relations_already_seen,
                            mappings_already_seen=mappings_already_seen,
                            data_collector=data_collector,
                            model=model,
                            freq=freq,
                            top_suggestions=top_suggestions,
                            domain=first_domain,
                            cache=cache,
                            num_of_suggestions=num_of_suggestions,
                        )
                    
            for solution in solutions: # TODO: fix here
                if not solution.top_suggestions:
                    solution.top_suggestions = top_suggestions
            


def mapping_suggestions_wrapper(
    base: List[str], 
    target: List[str],
    suggestions: bool,
    num_of_suggestions: int,
    solutions: List[Solution],
    data_collector: DataCollector,
    model: SentenceEmbedding,
    freq: Frequencies,
    mappings_already_seen: Set[Tuple[Tuple[Pair]]],
    relations_already_seen: Set[Tuple[str]],
    cache: dict,
    verbose: bool
    ) -> List[Solution]:
    # array of addition solutions for the suggestions if some entities have missing mappings.
    suggestions_solutions = []
    if suggestions and num_of_suggestions > 0:
        solutions = sorted(solutions, key=lambda x: (x.length, x.score), reverse=True)
        if solutions and solutions[0].length < max(len(base), len(target)):
            
            # this parameter allows us to look not only on the best result.
            # this relevant when the suggestion is for a strong one.
            # for example, if B=[earth, gravity], T=[nucleus, electron, electricity].
            # The best solution may hold earth:gravity~nucleus:electricity, but this
            # is only because 'sun' is not in the picture, yet. 
            number_of_solutions_for_suggestions = 3
            
            # the idea is to iterate over the founded solutions, and check if there are entities that not mapped.
            for solution in solutions[:number_of_solutions_for_suggestions]:
                if solution.length < max(len(base), len(target)) - 1:
                    # this logic is checked only if ONE entity have missing mapping (from base or target)
                    # the complication for two or more missing entities is too complicated. Better to asked
                    # from the user to be more specific.
                    continue
                
                mapping_suggestions(domain=base, 
                                    first_domain="actual_base", 
                                    second_domain="actual_target", 
                                    solution=solution, 
                                    data_collector=data_collector, 
                                    model=model, 
                                    freq=freq, 
                                    solutions=suggestions_solutions, 
                                    mappings_already_seen=mappings_already_seen,
                                    relations_already_seen=relations_already_seen,
                                    cache=cache, 
                                    num_of_suggestions=num_of_suggestions, 
                                    verbose=verbose)
                
                mapping_suggestions(domain=target, 
                                    first_domain="actual_target", 
                                    second_domain="actual_base", 
                                    solution=solution, 
                                    data_collector=data_collector, 
                                    model=model, 
                                    freq=freq, 
                                    solutions=suggestions_solutions, 
                                    mappings_already_seen=mappings_already_seen,
                                    relations_already_seen=relations_already_seen,
                                    cache=cache, 
                                    num_of_suggestions=num_of_suggestions, 
                                    verbose=verbose)                
    return suggestions_solutions
        

if __name__ == '__main__':
    res = get_best_matches_for_entity("newton", ["faraday", "sky", "window", "paper", "photo", "apple", "tomato", "wall", "home", "horse"])
    print(res)