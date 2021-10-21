import os
import copy
from pathlib import Path
from itertools import combinations
from typing import List, Dict, Tuple, Optional, Union, Set

from tqdm import tqdm
from click import secho

from utils import utils
from . import suggest_entities
from .quasimodo import Quasimodo
from frequency.frequency import Frequencies
from .data_collector import DataCollector
from utils.sentence_embadding import SentenceEmbedding

Pair = Tuple[str, str] # two entities: (b1,b2)
SingleMatch = List[Pair] # [(b1,b2), (t1,t2)]

root = Path(__file__).resolve().parent.parent.parent

NUM_OF_CLUSTERS_TO_CALC = 3
EDGE_THRESHOLD = 0.2
DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS = 0.8
FREQUENCY_THRESHOLD = 500

class Solution:
    def __init__(self, 
                mapping: List[str], 
                relations: List[SingleMatch], 
                scores: List[float], 
                score: float, 
                actual_base: List[str], 
                actual_target: List[str], 
                actual_indecies: Dict[str, Dict[str, int]], 
                length: int,
                coverage: List[int],
                availables: List[List[SingleMatch]] = None,
                sorted_results: List[Dict[str, Union[int, SingleMatch]]] = None
                ):
        self.mapping = mapping
        self.relations = relations
        self.scores = scores
        self.score = score
        self.actual_base = actual_base
        self.actual_target = actual_target
        self.actual_indecies = actual_indecies
        self.length = length
        self.top_suggestions = []
        self.availables = availables
        self.sorted_results = sorted_results
        self.coverage = coverage
    
    def get_actual(self, which: str):
        if which == 'actual_base':
            return self.actual_base
        elif which == 'actual_target':
            return self.actual_target
    
    def print_solution(self):
        secho("mapping", fg="blue", bold=True)
        for mapping in self.mapping:
            secho(f"\t{mapping}", fg="blue")
        print()

        secho("relations", fg="blue", bold=True)
        for relations, score, coverage in zip(self.relations, self.scores, self.coverage):
            secho(f"\t{relations},   ", fg="blue", nl=False)
            secho(f"Score: {score},  ", fg="blue", bold=True, nl=False)
            secho(f"Coverage: {coverage}", fg="blue", bold=True)
        print()

        secho(f"Score: {round(self.score, 3)}", fg="blue", bold=True)
        secho(f"Coverage: {sum(self.coverage)}", fg="blue", bold=True)
        print()


def get_edge_score(prop1: str, prop2: str, model: SentenceEmbedding, freq: Frequencies) -> float:
    if prop1 in freq.stopwords or prop2 in freq.stopwords:
        return 0
    else:
        return model.similarity(prop1, prop2)
    

def get_all_possible_pairs_map(base: List[str], target: List[str]) -> List[List[SingleMatch]]:
    # complexity: (n choose 2) * (n choose 2) * 2

    base_comb = list(combinations(base, 2))
    target_comb = list(combinations(target, 2))
    target_comb += [(val[1], val[0]) for val in target_comb]

    all_mapping = []
    for base_pair in base_comb:
        for target_pair in target_comb:
            all_mapping.append([
                [(base_pair[0], base_pair[1]), (target_pair[0], target_pair[1])],
                [(base_pair[1], base_pair[0]), (target_pair[1], target_pair[0])]
            ])

    return all_mapping


def check_if_valid(first_direction: SingleMatch, 
                   base_already_mapping: List[str],
                   base_already_mapping_as_set: Set[str],
                   target_already_mapping: List[str],
                   target_already_mapping_as_set: Set[str], 
                   actual_mapping_indecies: Dict[str, Dict[str, int]]
                   ) -> bool:
    b1, b2 = first_direction[0][0], first_direction[0][1]
    t1, t2 = first_direction[1][0], first_direction[1][1]

    if b1 in base_already_mapping_as_set and b2 in base_already_mapping_as_set:
        # we already map base1 and base2
        return False
    
    if b1 in base_already_mapping_as_set:
        if t1 != target_already_mapping[actual_mapping_indecies['base'][b1]]:
            # the match of mapping that already mapped is not true (base1->target1)
            return False
    
    if b2 in base_already_mapping_as_set:
        if t2 != target_already_mapping[actual_mapping_indecies['base'][b2]]:
            # the match of mapping that already mapped is not true (base2->target2)
            return False
    
    if t1 in target_already_mapping_as_set and t2 in target_already_mapping_as_set:
        # we already map target1 and target2
        return False

    if t1 in target_already_mapping_as_set:
        if b1 != base_already_mapping[actual_mapping_indecies['target'][t1]]:
            # the match of mapping that already mapped is not true (base1->target1)
            return False
    
    if t2 in target_already_mapping_as_set:
        if b2 != base_already_mapping[actual_mapping_indecies['target'][t2]]:
            # the match of mapping that already mapped is not true (base2->target2)
            return False
    
    return True


def update_paris_map(pairs_map: List[List[SingleMatch]], 
                     base_already_mapping: List[str], 
                     target_already_mapping: List[str], 
                     actual_mapping_indecies: Dict[str, Dict[str, int]]
                     ) -> List[List[SingleMatch]]:
    # This is List[SingleMatch] because there is two directions. But actully this is SingleMatch.
    return [mapping for mapping in pairs_map 
            if check_if_valid(mapping[0], 
                              base_already_mapping, 
                              set(base_already_mapping), 
                              target_already_mapping, 
                              set(target_already_mapping), 
                              actual_mapping_indecies)
            ]


def get_edges_with_maximum_weight(similatiry_edges: List[Tuple[str, str, float]], 
                                clustered_sentences_1: Dict[int, List[str]], 
                                clustered_sentences_2: Dict[int, List[str]]
                                ) -> Dict[Tuple[int, int], Tuple[str, str, float]]:
    # the idea here is for each two clusters (from the base and target) to take only one edge, which is the maximum weighted.
    cluster_edges_weights = {}
    for edge in similatiry_edges:
        cluster1, cluster2 = None, None
        for key, cluster in clustered_sentences_1.items():
            if edge[0] in cluster:
                cluster1 = int(key)
                break
        for key, cluster in clustered_sentences_2.items():
            if edge[1] in cluster:
                cluster2 = int(key) + len(clustered_sentences_1)
                break

        if (cluster1, cluster2) not in cluster_edges_weights:
            cluster_edges_weights[(cluster1, cluster2)] = edge
        else:
            if edge[2] > cluster_edges_weights[(cluster1, cluster2)][2]:
                cluster_edges_weights[(cluster1, cluster2)] = edge

    return cluster_edges_weights


def get_pair_mapping(model: SentenceEmbedding, data_collector: DataCollector, freq: Frequencies, mapping: SingleMatch):

    props_edge1 = data_collector.get_entities_relations(mapping[0][0], mapping[0][1])
    props_edge2 = data_collector.get_entities_relations(mapping[1][0], mapping[1][1])

    if not props_edge1 or not props_edge2:
        return {}

    # we want the weight of each edge between two nodes.
    similatiry_edges = [(prop1, prop2, get_edge_score(prop1, prop2, model, freq)) for prop1 in props_edge1 for prop2 in props_edge2]

    # we want the cluster similar properties
    clustered_sentences_1: Dict[int, List[str]] = model.clustering(mapping[0], distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)
    clustered_sentences_2: Dict[int, List[str]] = model.clustering(mapping[1], distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)

    # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
    cluster_edges_weights = get_edges_with_maximum_weight(similatiry_edges, clustered_sentences_1, clustered_sentences_2)
        
    # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
    # we will look only on edges that appear in cluster_edges_weights
    edges = utils.get_maximum_weighted_match(model, clustered_sentences_1, clustered_sentences_2, weights=cluster_edges_weights)
    edges = sorted(edges, key=lambda x: x[2], reverse=True)
    return {
        "graph": edges,
        "clusters1": clustered_sentences_1,
        "clusters2": clustered_sentences_2,
        "score": round(sum([edge[2] for edge in edges[:NUM_OF_CLUSTERS_TO_CALC] if edge[2] > EDGE_THRESHOLD]), 3)
    }


def get_best_pair_mapping_for_current_iteration(available_maps: List[List[SingleMatch]], 
                                                initial_results: List[Dict[str, Union[int, SingleMatch]]], 
                                                depth: int):
    available_maps_flatten = set()
    for available_map in available_maps:
        available_maps_flatten.add(tuple(available_map[0]))
        available_maps_flatten.add(tuple(available_map[1]))
    
    modified_results = [result for result in initial_results if tuple(result["best_mapping"]) in available_maps_flatten]
    results_for_current_iteration = [result for result in modified_results[:depth]]
    return results_for_current_iteration, modified_results


def get_best_pair_mapping(model: SentenceEmbedding, 
                          freq: Frequencies, 
                          data_collector: DataCollector, 
                          available_maps: List[List[SingleMatch]], 
                          cache: dict, 
                          depth: int = 0
                        ) -> List[Dict[str, Union[int, SingleMatch]]]:
    
    mappings = []
    # we will iterate over all the possible pairs mapping ((n choose 2)*(n choose 2)*2), 2->2, 3->18, 4->72
    iterator = available_maps if os.environ.get('CI', False) else tqdm(available_maps)
    for mapping in iterator:
        
        # for each mapping we want both direction, for example:
        # if we have in the base: earth, sun. AND in the target: electrons, nucleus.
        # for the mapping earth->electrons, sun->nucleus , we will calculate: 
        # earth .* sun, electrons .* nucleus AND sun .* earth, nucleus .* electrons
        mapping_score = 0
        coverage = 0
        for direction in mapping:
            b1, b2 = direction[0][0], direction[0][1]
            t1, t2 = direction[1][0], direction[1][1]
            props_edge1 = data_collector.get_entities_relations(b1, b2)
            props_edge2 = data_collector.get_entities_relations(t1, t2)

            if not props_edge1 or not props_edge2:
                continue

            # we want the weight of each edge between two nodes.
            similatiry_edges = [(prop1, prop2, get_edge_score(prop1, prop2, model, freq)) for prop1 in props_edge1 for prop2 in props_edge2]

            # we want the cluster similar properties
            clustered_sentences_1: Dict[int, List[str]] = model.clustering(direction[0], distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)
            clustered_sentences_2: Dict[int, List[str]] = model.clustering(direction[1], distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)

            # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
            cluster_edges_weights = get_edges_with_maximum_weight(similatiry_edges, clustered_sentences_1, clustered_sentences_2)
                
            # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
            # we will look only on edges that appear in cluster_edges_weights
            edges = utils.get_maximum_weighted_match(model, clustered_sentences_1, clustered_sentences_2, weights=cluster_edges_weights)
            edges = sorted(edges, key=lambda x: x[2], reverse=True)
            
            # score is just the sum of all the edges (edges between clusters)
            mapping_score += round(sum([edge[2] for edge in edges[:NUM_OF_CLUSTERS_TO_CALC] if edge[2] > EDGE_THRESHOLD]), 3)
            
            # coverage messure
            coverage += min(len(props_edge1), len(props_edge2))

        mappings.append((mapping[0], mapping_score, coverage))
        cache[((mapping[0][0][0], mapping[0][0][1]),(mapping[0][1][0], mapping[0][1][1]))] = mapping_score
        cache[((mapping[1][0][0], mapping[1][0][1]),(mapping[1][1][0], mapping[1][1][1]))] = mapping_score

    mappings = sorted(mappings, key=lambda x: x[1], reverse=True)
    if depth > 0:
        mappings = mappings[:depth]
    return [
        {
            "best_mapping": mapping[0], 
            "best_score": mapping[1],
            "coverage": mapping[2],
        } 
        for mapping in mappings]


def get_score(base: List[str], target: List[str], base_entity: str, target_entity: str, cache: dict) -> float:
    return round(sum([cache[((b, base_entity),(t, target_entity))] for b, t in zip(base, target)]), 3)


def update_already_mapping(b: str, t: str, B: List[str], T: List[str], indecies: Dict[str, Dict[str, int]]):
    B.append(b)
    T.append(t)
    # using for quick exists-check
    indecies['base'][b] = len(B) - 1
    indecies['target'][t] = len(T) - 1


def dfs(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    freq: Frequencies,
    curr_solution: Solution,
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    cache: dict,
    calls: List[int], # debug
    depth: int = 2):

    calls[0] += 1 # just to print the total recursive calls
    if curr_solution.actual_base:
        # first we will check if this node already seen in different variation
        relations_as_tuple = tuple([tuple(relation) for relation in sorted(curr_solution.relations)])
        if relations_as_tuple in relations_already_seen:
            return
        mapping_repr = [f"{b} --> {t}" for b, t in zip(curr_solution.actual_base, curr_solution.actual_target)]
        mapping_repr_as_tuple = tuple(sorted(mapping_repr))
        if mapping_repr_as_tuple in mappings_already_seen:
            return
        
        # the following sets using only for quick exists-check.
        relations_already_seen.add(relations_as_tuple)
        mappings_already_seen.add(mapping_repr_as_tuple)
        curr_solution.mapping = mapping_repr
        # new solution
        # in the end we will sort by the length and the score. So its ok to add all solutions
        solutions.append(curr_solution)

    # base case for recursive function. there is no more available pairs to match (base->target)
    if len(curr_solution.actual_base) == min(len(base), len(target)):
        return

    # we will get the top-depth pairs with the best score.
    best_results_for_current_iteration, modified_results = get_best_pair_mapping_for_current_iteration(curr_solution.availables, curr_solution.sorted_results, depth)
    for result in best_results_for_current_iteration:
        # if the best score is > 0, we will update the base and target lists of the already mapping entities.
        # otherwise, if the best score is 0, we have no more mappings to do.
        if result["best_score"] > 0:
            # deepcopy is more safe when working with recursive functions
            solution_copy = copy.deepcopy(curr_solution)
            solution_copy.relations.append(result["best_mapping"])
            solution_copy.scores.append(round(result["best_score"], 3))
            solution_copy.coverage.append(result["coverage"])

            # we will add the new mapping to the already mapping lists. They must be in the same shape.
            b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
            t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
            score = 0
            if b1 not in solution_copy.actual_base and t1 not in solution_copy.actual_target:
                score += get_score(solution_copy.actual_base, solution_copy.actual_target, b1, t1, cache)
                update_already_mapping(b1, t1, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

            if b2 not in solution_copy.actual_base and t2 not in solution_copy.actual_target:
                score += get_score(solution_copy.actual_base, solution_copy.actual_target, b2, t2, cache)
                update_already_mapping(b2, t2, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
            
            solution_copy.score += round(score, 3)
            
            # here we update the possible/available pairs.
            # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
            # pairs that already maps. in our example it can be one of the following:
            # (a->1, c->3) or (b->2, c->3).
            solution_copy.availables = update_paris_map(solution_copy.availables, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
            solution_copy.length = len(solution_copy.actual_base)
            solution_copy.sorted_results = modified_results
            
            dfs(
                base=base, 
                target=target,
                solutions=solutions,
                freq=freq,
                curr_solution=solution_copy,
                relations_already_seen=relations_already_seen,
                mappings_already_seen=mappings_already_seen,
                cache=cache,
                calls=calls,
                depth=depth
            )
    

def mapping_suggestions(
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
    # this function is use for mapping in suggestions mode. this is only one iteration.
    
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
                score += get_score(base_already_mapping_new, target_already_mapping_new, b1, t1, cache)
                update_already_mapping(b1, t1, base_already_mapping_new, target_already_mapping_new, actual_mapping_indecies_new)
            
            if b2 not in base_already_mapping_new and t2 not in target_already_mapping_new:
                score += get_score(base_already_mapping_new, target_already_mapping_new, b2, t2, cache)
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


def mapping_suggestions_wrapper(
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
        entities_suggestions: List[str] = suggest_entities.get_suggestions_for_missing_entities(
                                                                                                data_collector, 
                                                                                                first_domain_not_mapped_entity, 
                                                                                                solution.get_actual(first_domain), 
                                                                                                solution.get_actual(second_domain), 
                                                                                                verbose=verbose)
        if not entities_suggestions:
            continue  # no suggestion found :(
        if first_domain == "actual_base":
            new_base = solution.get_actual("actual_base") + [first_domain_not_mapped_entity]
            new_target = solution.get_actual("actual_target") + entities_suggestions
        elif first_domain == "actual_target":
            new_base = solution.get_actual("actual_base") + entities_suggestions
            new_target = solution.get_actual("actual_target") + [first_domain_not_mapped_entity]
            
        all_pairs = get_all_possible_pairs_map(new_base, new_target)
        available_pairs_new = update_paris_map(all_pairs, solution.get_actual("actual_base"), solution.get_actual("actual_target"), solution.actual_indecies)
        top_suggestions = []
        mapping_suggestions(
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


def beam_search(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    freq: Frequencies,
    cache: dict,
    N: int = 4):

    curr_solutions = []
    for solution in solutions:
        # we will get the top-depth pairs with the best score.
        best_results_for_current_iteration, modified_results = get_best_pair_mapping_for_current_iteration(solution.availables, solution.sorted_results, N)
        solution.sorted_results = modified_results
        for result in best_results_for_current_iteration:
            # if the best score is > 0, we will update the base and target lists of the already mapping entities.
            # otherwise, if the best score is 0, we have no more mappings to do.
            if result["best_score"] > 0:
                solution_copy = copy.deepcopy(solution)
                
                solution_copy.relations.append(result["best_mapping"])
                relations_as_tuple = tuple([tuple(relation) for relation in sorted(solution_copy.relations)])
                if relations_as_tuple in relations_already_seen:
                    continue
                relations_already_seen.add(relations_as_tuple)

                solution_copy.scores.append(round(result["best_score"], 3))
                solution_copy.coverage.append(result["coverage"])

                b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
                t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
                score = 0
                if b1 not in solution_copy.actual_base and t1 not in solution_copy.actual_target:
                    score += get_score(solution_copy.actual_base, solution_copy.actual_target, b1, t1, cache)
                    update_already_mapping(b1, t1, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

                if b2 not in solution_copy.actual_base and t2 not in solution_copy.actual_target:
                    score += get_score(solution_copy.actual_base, solution_copy.actual_target, b2, t2, cache)
                    update_already_mapping(b2, t2, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

                solution_copy.score += score
                mapping_repr = [f"{b} --> {t}" for b, t in zip(solution_copy.actual_base, solution_copy.actual_target)]
                mapping_repr_as_tuple = tuple(sorted(mapping_repr))
                if mapping_repr_as_tuple in mappings_already_seen:
                    continue
                mappings_already_seen.add(mapping_repr_as_tuple)

                solution_copy.mapping = mapping_repr

                # here we update the possible/available pairs.
                # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
                # pairs that already maps. in our example it can be one of the following:
                # (a->1, c->3) or (b->2, c->3).
                new_available_pairs = update_paris_map(solution_copy.availables, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
                solution_copy.availables = new_available_pairs
                solution_copy.length = len(solution_copy.actual_base)
                curr_solutions.append(solution_copy)

    if not curr_solutions:
        return
    
    solutions_ = sorted(solutions + curr_solutions, key=lambda x: (x.length, x.score), reverse=True)[:N]
    for i, solution_ in enumerate(solutions_):
        solutions[i] = solution_

    beam_search(
        base=base, 
        target=target,
        solutions=solutions,
        relations_already_seen=relations_already_seen,
        mappings_already_seen=mappings_already_seen,
        freq=freq,
        cache=cache,
        N=N
    )


def beam_search_wrapper(base: List[str], 
                        target: List[str], 
                        suggestions: bool = False, 
                        num_of_suggestions: int = 1,
                        N: int = 4, 
                        verbose: bool = False, 
                        quasimodo: Quasimodo = None, 
                        freq: Frequencies = None, 
                        model_name: str = 'msmarco-distilbert-base-v4',
                        threshold: Union[float, int] = FREQUENCY_THRESHOLD) -> List[Solution]:

    # we want all the possible pairs.
    # general there are (n choose 2) * (n choose 2) * 2 pairs.
    available_pairs = get_all_possible_pairs_map(base, target)

    # better to init all the objects here, since they are not changed in the run
    if not quasimodo:
        quasimodo = Quasimodo()
    data_collector = DataCollector(quasimodo=quasimodo)
    model = SentenceEmbedding(model=model_name, data_collector=data_collector)
    if not freq:
        json_folder = root / 'backend' / 'frequency' /  'jsons' / 'merged' / '20%'
        json_basename = 'ci.json' if 'CI' in os.environ else 'all_1m_filter_3_sort.json'
        freq = Frequencies(json_folder / json_basename, threshold=threshold)

    cache = {}
    best_results = get_best_pair_mapping(model, freq, data_collector, available_pairs, cache)

    # this is an array of solutions we going to update in the mapping function.
    solutions = []
    for i in range(N):
        solutions.append(
            Solution(
                mapping=[], 
                relations=[], 
                scores=[], 
                score=0, 
                actual_base=[], 
                actual_target=[], 
                actual_indecies={'base': {}, 'target': {}}, 
                length=0,
                coverage=[],
                availables=copy.deepcopy(available_pairs),
                sorted_results=copy.deepcopy(best_results)
            )
        )

    mappings_already_seen = set()
    relations_already_seen = set()
    beam_search(base=base, 
                target=target, 
                solutions=solutions, 
                mappings_already_seen=mappings_already_seen,
                relations_already_seen=relations_already_seen,
                freq=freq, 
                cache=cache, 
                N=N)
    
    # array of addition solutions for the suggestions if some entities have missing mappings.
    suggestions_solutions = []
    if suggestions and num_of_suggestions > 0:
        solutions = sorted(solutions, key=lambda x: (x.length, x.score), reverse=True)
        if solutions and solutions[0].length < max(len(base), len(target)):
            number_of_solutions_for_suggestions = 1
            # the idea is to iterate over the founded solutions, and check if there are entities are not mapped.
            for solution in solutions[:number_of_solutions_for_suggestions]:
                if solution.length < max(len(base), len(target)) - 1:
                    # this logic is checked only if ONE entity have missing mapping (from base or target)
                    continue
                
                mapping_suggestions_wrapper(domain=base, 
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
                
                mapping_suggestions_wrapper(domain=target, 
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

    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: (x.length, x.score), reverse=True)
    if not all_solutions:
        if verbose:
            secho("No solution found")
        return []
    if verbose:
        secho(f"\nBase: {base}", fg="blue", bold=True)
        secho(f"Target: {target}\n", fg="blue", bold=True)
        for i, solution in enumerate(all_solutions[:10]):
            if solution.score == 0:
                break
            secho(f"#{i+1}", fg="blue", bold=True)
            solution.print_solution()

    return all_solutions


def mapping_wrapper(base: List[str], 
                    target: List[str], 
                    suggestions: bool = True, 
                    depth: int = 2, 
                    top_n: int = 10, 
                    num_of_suggestions: int = 1, 
                    verbose: bool = False, 
                    quasimodo: Quasimodo = None, 
                    freq: Frequencies = None, 
                    model_name: str = 'msmarco-distilbert-base-v4',
                    threshold: Union[float, int] = FREQUENCY_THRESHOLD) -> List[Solution]:

    # we want all the possible pairs.
    # general there are (n choose 2) * (n choose 2) * 2 pairs.
    available_pairs = get_all_possible_pairs_map(base, target)

    # this is an array of solutions we going to update in the mapping function.
    solutions = []

    # better to init all the objects here, since they are not changed in the run
    if not quasimodo:
        quasimodo = Quasimodo()
    data_collector = DataCollector(quasimodo=quasimodo)
    model = SentenceEmbedding(model=model_name, data_collector=data_collector)
    if not freq:
        json_folder = root / 'backend' / 'frequency' /  'jsons' / 'merged' / '20%'
        json_basename = 'ci.json' if 'CI' in os.environ else 'all_1m_filter_3_sort.json'
        freq = Frequencies(json_folder / json_basename, threshold=threshold)

    cache = {}
    calls = [0]
    best_results = get_best_pair_mapping(model, freq, data_collector, available_pairs, cache)
    initial_solution = Solution(
                            mapping=[], 
                            relations=[], 
                            scores=[], 
                            score=0, 
                            actual_base=[], 
                            actual_target=[], 
                            actual_indecies={'base': {}, 'target': {}}, 
                            length=0,
                            coverage=[],
                            sorted_results=best_results,
                            availables=copy.deepcopy(available_pairs)
                        )
    
    mappings_already_seen = set()
    relations_already_seen = set()
    dfs(base=base, 
        target=target, 
        solutions=solutions, 
        freq=freq, 
        curr_solution=initial_solution,
        relations_already_seen=relations_already_seen, 
        mappings_already_seen=mappings_already_seen, 
        cache=cache, 
        calls=calls, 
        depth=depth)

    # array of addition solutions for the suggestions if some entities have missing mappings.
    suggestions_solutions = []
    if suggestions and num_of_suggestions > 0:
        solutions = sorted(solutions, key=lambda x: (x.length, x.score), reverse=True)
        if solutions and solutions[0].length < max(len(base), len(target)):
            number_of_solutions_for_suggestions = 1
            # the idea is to iterate over the founded solutions, and check if there are entities are not mapped.
            for solution in solutions[:number_of_solutions_for_suggestions]:
                if solution.length < max(len(base), len(target)) - 1:
                    # this logic is checked only if ONE entity have missing mapping (from base or target)
                    continue
                
                mapping_suggestions_wrapper(domain=base, 
                                            first_domain="actual_base", 
                                            second_domain="actual_target", 
                                            solution=solution, 
                                            data_collector=data_collector, 
                                            model=model, 
                                            freq=freq, 
                                            solutions=suggestions_solutions, 
                                            relations_already_seen=relations_already_seen, 
                                            mappings_already_seen=mappings_already_seen, 
                                            cache=cache, 
                                            num_of_suggestions=num_of_suggestions, 
                                            verbose=verbose)
                
                mapping_suggestions_wrapper(domain=target, 
                                            first_domain="actual_target", 
                                            second_domain="actual_base", 
                                            solution=solution, 
                                            data_collector=data_collector, 
                                            model=model, 
                                            freq=freq, 
                                            solutions=suggestions_solutions, 
                                            relations_already_seen=relations_already_seen, 
                                            mappings_already_seen=mappings_already_seen, 
                                            cache=cache, 
                                            num_of_suggestions=num_of_suggestions, 
                                            verbose=verbose)

    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: (x.length, x.score), reverse=True)
    if not all_solutions:
        if verbose:
            secho("No solution found")
        return []
    if verbose:
        secho(f"\nBase: {base}", fg="blue", bold=True)
        secho(f"Target: {target}\n", fg="blue", bold=True)
        solutions_to_print = 10 if os.environ.get('CI', False) else top_n
        for i, solution in enumerate(all_solutions[:solutions_to_print]):
            secho(f"#{i+1}", fg="blue", bold=True)
            solution.print_solution()

    secho(f"Number of recursive calls: {calls[0]}\n")
    return all_solutions[:top_n]


if __name__ == "__main__":
    # os.environ['CI'] = 'true'

    # 20x20
    base = ['sun', 'planet', 'orbit', 'kepler', 'moon', 'jupiter', 'comet', 'equator', 'zodiac', 'saturn', 'venus', 'neptune', 'pluto', 'nebula', 'eccentricity', 'earth', 'radius', 'eclipse', 'astronomer', 'asteroid']
    target = ['nucleus', 'electrons', 'proton', 'neutron', 'atom', 'excitation', 'resonance', 'photon', 'dipole', 'scattering', 'valence', 'helium', 'coupling', 'decay', 'particle', 'spin', 'spectroscopy', 'hydrogen', 'phosphorylation', 'gamma']
    
    base = base[:18]
    target = target[:18]
    # solutions = mapping_wrapper(base, target, suggestions=False, depth=4, top_n=20, verbose=True)
    solutions = beam_search_wrapper(base, target, suggestions=False, N=20, verbose=True)
