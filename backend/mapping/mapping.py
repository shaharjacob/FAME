import os
from pathlib import Path
from itertools import combinations
from typing import List, Dict, Tuple, Union, Set, Callable

from tqdm import tqdm
from click import secho

from utils import utils
from .quasimodo import Quasimodo
from frequency.frequency import Frequencies
from .data_collector import DataCollector
from utils.sentence_embadding import SentenceEmbedding

Pair = Tuple[str, str] # two entities: (b1,b2)
SingleMatch = List[Pair] # [(b1,b2), (t1,t2)]
ScoreCache = Dict[Tuple[Tuple[str, str], Tuple[str, str]], float]
MappingCache = Set[Tuple[Tuple[Pair]]]
RelationCache = Set[Tuple[str]]
Cache = Union[ScoreCache, MappingCache, RelationCache]
Unmutables = Union[Quasimodo, DataCollector, SentenceEmbedding, Frequencies]

root = Path(__file__).resolve().parent.parent.parent

NUM_OF_CLUSTERS_TO_CALC = 3
EDGE_THRESHOLD = 0.2
DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS = 0.5
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
        secho("Mapping", fg="blue", bold=True)
        for mapping in self.mapping:
            secho(f"\t{mapping}", fg="blue")
        print()

        secho("Relations", fg="blue", bold=True)
        for relations, score, coverage in zip(self.relations, self.scores, self.coverage):
            secho(f"\t{relations},   ", fg="blue", nl=False)
            secho(f"Score: {score},  ", fg="blue", bold=True, nl=False)
            secho(f"Coverage: {coverage}", fg="blue", bold=True)
        print()

        if self.top_suggestions:
            secho("Suggestions", fg="blue", bold=True)
            secho(f"\t{self.top_suggestions}", fg="blue")
            print()

        secho(f"Score: {round(self.score, 3)}", fg="blue", bold=True)
        secho(f"Coverage: {sum(self.coverage)}", fg="blue", bold=True)
        print()


def print_results(base: List[str], target: List[str], solutions: List[Solution]):
    secho(f"\nBase: {base}", fg="blue", bold=True)
    secho(f"Target: {target}\n", fg="blue", bold=True)
    if solutions:
        for i, solution in enumerate(solutions):
            if solution.score == 0:
                break
            secho(f"#{i+1}", fg="blue", bold=True)
            solution.print_solution()
    else:
        secho("No solution found")


def mapping_wrapper(func: Callable, **kwargs) -> List[Solution]:
    return func(**kwargs)


def get_edge_score(prop1: str, prop2: str, model: SentenceEmbedding, freq: Frequencies) -> float:
    if prop1 in freq.stopwords or prop2 in freq.stopwords:
        return 0
    else:
        return model.similarity(prop1, prop2)


def get_score(base: List[str], target: List[str], base_entity: str, target_entity: str, cache: ScoreCache) -> float:
    # we take the score of the new b->t with all the others. 
    # i.e. we will take the score of b_i:b~t_i:t.
    return round(sum([cache[((b, base_entity),(t, target_entity))] for b, t in zip(base, target)]), 3)


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
    clustered_sentences_1: Dict[int, List[str]] = model.clustering(props_edge1, distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)
    clustered_sentences_2: Dict[int, List[str]] = model.clustering(props_edge2, distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)

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


def get_best_pair_mapping_for_current_iteration(
    available_maps: List[List[SingleMatch]], 
    initial_results: List[Dict[str, Union[int, SingleMatch]]], 
    depth: int
    ) -> Tuple[List[Dict[str, Union[int, SingleMatch]]], List[Dict[str, Union[int, SingleMatch]]]]:

    # better to iterate one time over the available_maps and store it in a set
    available_maps_flatten = set()
    for available_map in available_maps:
        available_maps_flatten.add(tuple(available_map[0]))
        available_maps_flatten.add(tuple(available_map[1]))
    
    # modified_results important for the next iteration
    modified_results = [result for result in initial_results if tuple(result["best_mapping"]) in available_maps_flatten]
    results_for_current_iteration = [result for result in modified_results[:depth]]
    return results_for_current_iteration, modified_results


def get_best_pair_mapping(
    unmutables: Dict[str, Unmutables],
    available_maps: List[List[SingleMatch]], 
    cache: Dict[str, Cache], 
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
            props_edge1 = unmutables["data_collector"].get_entities_relations(b1, b2)
            props_edge2 = unmutables["data_collector"].get_entities_relations(t1, t2)

            if not props_edge1 or not props_edge2:
                continue

            # we want the weight of each edge between two nodes.
            similatiry_edges = [(prop1, prop2, get_edge_score(prop1, prop2, unmutables["model"], unmutables["freq"])) for prop1 in props_edge1 for prop2 in props_edge2]

            # we want the cluster similar properties
            clustered_sentences_1: Dict[int, List[str]] = unmutables["model"].clustering(props_edge1, distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)
            clustered_sentences_2: Dict[int, List[str]] = unmutables["model"].clustering(props_edge2, distance_threshold=DEFAULT_DIST_THRESHOLD_FOR_CLUSTERS)

            # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
            cluster_edges_weights = get_edges_with_maximum_weight(similatiry_edges, clustered_sentences_1, clustered_sentences_2)
                
            # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
            # we will look only on edges that appear in cluster_edges_weights
            edges = utils.get_maximum_weighted_match(unmutables["model"], clustered_sentences_1, clustered_sentences_2, weights=cluster_edges_weights)
            edges = sorted(edges, key=lambda x: x[2], reverse=True)
            
            # score is just the sum of all the edges (edges between clusters)
            mapping_score += round(sum([edge[2] for edge in edges[:NUM_OF_CLUSTERS_TO_CALC] if edge[2] > EDGE_THRESHOLD]), 3)
            
            # coverage messure
            coverage += min(len(props_edge1), len(props_edge2))

        mappings.append((mapping[0], mapping_score, coverage))
        cache["scores"][((mapping[0][0][0], mapping[0][0][1]),(mapping[0][1][0], mapping[0][1][1]))] = mapping_score
        cache["scores"][((mapping[1][0][0], mapping[1][0][1]),(mapping[1][1][0], mapping[1][1][1]))] = mapping_score

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


def update_already_mapping(b: str, t: str, B: List[str], T: List[str], indecies: Dict[str, Dict[str, int]]):
    B.append(b)
    T.append(t)
    # using for quick exists-check
    indecies['base'][b] = len(B) - 1
    indecies['target'][t] = len(T) - 1


def set_unmutables(unmutables: Dict[str, Union[Quasimodo, DataCollector, SentenceEmbedding, Frequencies]], args: dict):
    if not unmutables:
        unmutables["quasimodo"] = Quasimodo()
        unmutables["data_collector"] = DataCollector(api=args, quasimodo=unmutables["quasimodo"])
        unmutables["model"] = SentenceEmbedding(model=args["model_name"])
        json_folder = root / 'backend' / 'frequency'
        unmutables["freq"] = Frequencies(json_folder / 'freq.json', threshold=args["freq_th"])

