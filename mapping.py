import copy
from itertools import combinations
from typing import List, Dict, Tuple, Optional

from tqdm import tqdm
from click import secho

import utils
import suggest_entities
from quasimodo import Quasimodo
from data_collector import DataCollector
from sentence_embadding import SentenceEmbedding


def get_all_possible_pairs_map(base: List[str], target: List[str]) -> List[List[List[Tuple[str, str]]]]:
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


def update_paris_map(pairs_map: List[List[List[Tuple[str, str]]]], base_already_mapping: List[str], target_already_mapping: List[str]) -> List[List[List[Tuple[str, str]]]]:
    new_pairs_map = []
    for mapping in pairs_map:
        one_direction = mapping[0]

        if one_direction[0][0] in base_already_mapping and one_direction[0][1] in base_already_mapping:
            # we already map base1 and base2
            continue
        
        if one_direction[0][0] in base_already_mapping:
            if one_direction[1][0] != target_already_mapping[base_already_mapping.index(one_direction[0][0])]:
                # the match of mapping that already mapped is not true (base1->target1)
                continue
        
        if one_direction[0][1] in base_already_mapping:
            if one_direction[1][1] != target_already_mapping[base_already_mapping.index(one_direction[0][1])]:
                # the match of mapping that already mapped is not true (base2->target2)
                continue
        
        if one_direction[1][0] in target_already_mapping and one_direction[1][1] in target_already_mapping:
            # we already map target1 and target2
            continue

        if one_direction[1][0] in target_already_mapping:
            if one_direction[0][0] != base_already_mapping[target_already_mapping.index(one_direction[1][0])]:
                # the match of mapping that already mapped is not true (base1->target1)
                continue
        
        if one_direction[1][1] in target_already_mapping:
            if one_direction[0][1] != base_already_mapping[target_already_mapping.index(one_direction[1][1])]:
                # the match of mapping that already mapped is not true (base2->target2)
                continue
        
        new_pairs_map.append(mapping)
    return new_pairs_map


def update_list(already_mapping_list: List[str], entities: Tuple[str, str], inplace: bool = False) -> Optional[List[str]]:
    list_to_update = already_mapping_list if inplace else copy.deepcopy(already_mapping_list)
    if entities[0] not in list_to_update:
        list_to_update.append(entities[0])
    if entities[1] not in list_to_update:
        list_to_update.append(entities[1])
    if not inplace:
        return list_to_update


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


def get_pair_mapping(model: SentenceEmbedding, data_collector: DataCollector, mapping: List[Tuple[str, str]]):

    props_edge1 = data_collector.get_entities_relations(mapping[0][0], mapping[0][1])
    props_edge2 = data_collector.get_entities_relations(mapping[1][0], mapping[1][1])

    if not props_edge1 or not props_edge2:
        return {}

    # we want the weight of each edge between two nodes.
    similatiry_edges = [(prop1, prop2, model.similarity(prop1, prop2)) for prop1 in props_edge1 for prop2 in props_edge2]

    # we want the cluster similar properties
    clustered_sentences_1: Dict[int, List[str]] = model.clustering(mapping[0], distance_threshold=0.8)
    clustered_sentences_2: Dict[int, List[str]] = model.clustering(mapping[1], distance_threshold=0.8)

    # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
    cluster_edges_weights = get_edges_with_maximum_weight(similatiry_edges, clustered_sentences_1, clustered_sentences_2)
        
    # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
    # we will look only on edges that appear in cluster_edges_weights
    edges = utils.get_maximum_weighted_match(model, clustered_sentences_1, clustered_sentences_2, cluster_edges_weights)
    return {
        "graph": edges,
        "clusters1": clustered_sentences_1,
        "clusters2": clustered_sentences_2,
        "score": round(sum([edge[2] for edge in edges]), 3)
    }


def get_best_pair_mapping(model: SentenceEmbedding, data_collector: DataCollector, available_maps: List[List[List[Tuple[str, str]]]], depth: int = 2) -> Dict:
    mappings = []

    # we will iterate over all the possible pairs mapping ((n choose 2)*(n choose 2)*2), 2->2, 3->18, 4->72
    for mapping in tqdm(available_maps):
        # for each mapping we want both direction, for example:
        # if we have in the base: earth, sun. AND in the target: electrons, nucleus.
        # for the mapping earth->electrons, sun->nucleus , we will calculate: 
        # earth .* sun, electrons .* nucleus AND sun .* earth, nucleus .* electrons
        mapping_score = 0
        for direction in mapping:
            props_edge1 = data_collector.get_entities_relations(direction[0][0], direction[0][1])
            props_edge2 = data_collector.get_entities_relations(direction[1][0], direction[1][1])

            if not props_edge1 or not props_edge2:
                continue

            # we want the weight of each edge between two nodes.
            similatiry_edges = [(prop1, prop2, model.similarity(prop1, prop2)) for prop1 in props_edge1 for prop2 in props_edge2]

            # we want the cluster similar properties
            clustered_sentences_1: Dict[int, List[str]] = model.clustering(direction[0], distance_threshold=0.8)
            clustered_sentences_2: Dict[int, List[str]] = model.clustering(direction[1], distance_threshold=0.8)

            # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
            cluster_edges_weights = get_edges_with_maximum_weight(similatiry_edges, clustered_sentences_1, clustered_sentences_2)
                
            # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
            # we will look only on edges that appear in cluster_edges_weights
            edges = utils.get_maximum_weighted_match(model, clustered_sentences_1, clustered_sentences_2, cluster_edges_weights)
            
            # score is just the sum of all the edges (edges between clusters)
            mapping_score += round(sum([edge[2] for edge in edges]), 3)

        mappings.append((mapping[0], mapping_score))

    mappings = sorted(mappings, key=lambda x: x[1], reverse=True)
    return [{"best_mapping": mapping[0], "best_score": mapping[1]} for mapping in mappings[:depth]]


def mapping(
    base: List[str], 
    target: List[str],
    available_pairs: List[List[List[Tuple[str, str]]]],
    solutions: List[dict],
    data_collector: DataCollector,
    model: SentenceEmbedding,
    base_already_mapping: List[str],
    target_already_mapping: List[str],
    relations: List[List[Tuple[str, str]]],
    score: float,
    depth: int = 2):

    # base case for recursive function. there is no more available pairs to match (base->target)
    if len(base_already_mapping) == min(len(base), len(target)):
        solutions.append({
            "mapping": [f"{b} --> {t}" for b, t in zip(base_already_mapping, target_already_mapping)],
            "relations": relations,
            "score": round(score, 3),
            "actual_base": base_already_mapping,
            "actual_target": target_already_mapping,
        })
        return

    # we will get the top-depth pairs with the best score.
    best_results_for_current_iteration = get_best_pair_mapping(model, data_collector, available_pairs, depth)
    for result in best_results_for_current_iteration:
        # if the best score is > 0, we will update the base and target lists of the already mapping entities.
        # otherwise, if the best score is 0, we have no more mappings to do.
        if result["best_score"] > 0:
            # deepcopy is more safe when working with recursive functions
            available_pairs_copy = copy.deepcopy(available_pairs)
            relations_copy = copy.deepcopy(relations)
            relations_copy.append(result["best_mapping"])

            # we will add the new mapping to the already mapping lists. 
            base_already_mapping_new = update_list(base_already_mapping, (result["best_mapping"][0][0], result["best_mapping"][0][1]), inplace=False)
            target_already_mapping_new = update_list(target_already_mapping, (result["best_mapping"][1][0], result["best_mapping"][1][1]), inplace=False)
            
            # here we update the possible/available pairs.
            # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
            # pairs that already maps. in our example it can be one of the following:
            # (a->1, c->3) or (b->2, c->3).
            available_pairs_copy = update_paris_map(available_pairs_copy, base_already_mapping_new, target_already_mapping_new)
            
            mapping(
                base=base, 
                target=target,
                available_pairs=available_pairs_copy,
                solutions=solutions,
                data_collector=data_collector,
                model=model,
                base_already_mapping=base_already_mapping_new,
                target_already_mapping=target_already_mapping_new,
                relations=relations_copy,
                score=score+result["best_score"],
                depth=depth
            )
    

def mapping_suggestions(
    available_pairs: List[List[List[Tuple[str, str]]]],
    current_solution: dict,
    solutions: List[dict],
    data_collector: DataCollector,
    model: SentenceEmbedding,
    top_suggestions: List[str],
    num_of_suggestions: int = 1):
    # this function is use for mapping in suggestions mode. this is only one iteration.
    # we will get the top-num-of-suggestions with the best score.
    best_results_for_current_iteration = get_best_pair_mapping(model, data_collector, available_pairs, num_of_suggestions)
    for result in best_results_for_current_iteration:
        # if the best score is > 0, we will update the base and target lists of the already mapping entities.
        # otherwise, if the best score is 0, we have no more mappings to do.
        if result["best_score"] > 0:
            # we will add the new mapping to the already mapping lists. 
            base_already_mapping_new = update_list(current_solution["actual_base"], (result["best_mapping"][0][0], result["best_mapping"][0][1]), inplace=False)
            target_already_mapping_new = update_list(current_solution["actual_target"], (result["best_mapping"][1][0], result["best_mapping"][1][1]), inplace=False)
            
            # updating the top suggestions for the GUI
            top_suggestions.append(target_already_mapping_new[-1])
            
            # we need to add the mapping that we just found to the relations that already exist for that solution.
            relations = copy.deepcopy(current_solution["relations"])
            relations.append(result["best_mapping"])

            solutions.append({
                "mapping": [f"{b} --> {t}" for b, t in zip(base_already_mapping_new, target_already_mapping_new)],
                "relations": relations,
                "score": round(current_solution["score"] + result["best_score"], 3),
                "actual_base": base_already_mapping_new,
                "actual_target": target_already_mapping_new,
            })


def mapping_suggestions_wrapper(
    domain: List[str],
    first_domain: str, 
    second_domain: str, 
    solution: dict, 
    data_collector: DataCollector,
    model: SentenceEmbedding, 
    solutions: List[dict],
    num_of_suggestions: int = 1):
    
    first_domain_not_mapped_entities = [entity for entity in domain if entity not in solution[first_domain]]
    for first_domain_not_mapped_entity in first_domain_not_mapped_entities:
        # suggestion for mapping an entity. a list of strings.
        entities_suggestions = suggest_entities.get_suggestions_for_missing_entities(data_collector, first_domain_not_mapped_entity, solution[first_domain], solution[second_domain], verbose=False)
        if not entities_suggestions:
            continue  # no suggestion found :(
        if first_domain == "actual_base":
            new_base = solution["actual_base"] + [first_domain_not_mapped_entity]
            new_target = solution["actual_target"] + entities_suggestions
        else:  # first_domain == "actual_target"
            new_base = solution["actual_base"] + entities_suggestions
            new_target = solution["actual_target"] + [first_domain_not_mapped_entity]
            
        all_pairs = get_all_possible_pairs_map(new_base, new_target)
        available_pairs_new = update_paris_map(all_pairs, solution["actual_base"], solution["actual_target"])
        top_suggestions = []
        mapping_suggestions(
            available_pairs=available_pairs_new,
            current_solution=copy.deepcopy(solution),
            solutions=solutions,
            data_collector=data_collector,
            model=model,
            top_suggestions=top_suggestions,
            num_of_suggestions=num_of_suggestions,
        )
        for solution in solutions: # TODO: fix here
            solution["top_suggestions"] = solution.get("top_suggestions", top_suggestions)


def mapping_wrapper(base: List[str], target: List[str], suggestions: bool = True, depth: int = 2, top_n: int = 1, num_of_suggestions: int = 1, verbose: bool = False):

    # we want all the possible pairs.
    # general there are (n choose 2) * (n choose 2) * 2 pairs.
    available_pairs = get_all_possible_pairs_map(base, target)

    # this is an array of solutions we going to update in the mapping function.
    solutions = []

    # better to init all the objects here, since they are not changed in the run
    quasimodo = Quasimodo()
    data_collector = DataCollector(quasimodo=quasimodo)
    model = SentenceEmbedding(data_collector=data_collector)
    mapping(base, target, available_pairs, solutions, data_collector, model, [], [], [], 0, depth=depth)
    
    # array of addition solutions for the suggestions if some entities have missing mappings.
    suggestions_solutions = []
    if suggestions:
        # the idea is to iterate over the founded solutions, and check if there are entities are not mapped.
        # this logic is checked only if ONE entity have missing mapping (from base or target)
        for solution in solutions:
            mapping_suggestions_wrapper(base, "actual_base", "actual_target", solution, data_collector, model, suggestions_solutions, num_of_suggestions)
            mapping_suggestions_wrapper(target, "actual_target", "actual_base", solution, data_collector, model, suggestions_solutions, num_of_suggestions)
    
    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: x["score"], reverse=True)
    if verbose:
        for solution in all_solutions:
            print_solution(solution)
    return all_solutions[:top_n] if top_n > 1 else all_solutions[0]


def print_solution(solution: dict):
    secho("mapping", fg="blue", bold=True)
    for mapping in solution["mapping"]:
        secho(f"\t{mapping}", fg="blue")
    print()

    secho("relations", fg="blue", bold=True)
    for relations in solution["relations"]:
        secho(f"\t{relations}", fg="blue")
    print()

    secho(f"score: {solution['score']}", fg="blue", bold=True)
    print()
    print("------------------------------------------------------")
    print()


if __name__ == "__main__":
    base = ["earth", "gravity", "newton"]
    target = ["electrons", "nucleus", "electricity", "faraday"]
    solution = mapping_wrapper(base, target, depth=4, verbose=True)
    # print_solution(solution)
    



















    #  a->1, b->2, (a:b, 1:2)
    #  a->2, b->1, (a:b, 2:1)
    #  a->2, b->3, (a:b, 2:3)
    #  a->3, b->2, (a:b, 3:2)
    #  a->1, b->3, (a:b, 1:3)
    #  a->3, b->1, (a:b, 3:1)
    #  b->1, c->2, (b:c, 1:2)
    #  b->2, c->1, (b:c, 2:1)
    #  b->2, c->3, (b:c, 2:3)
    #  b->3, c->2, (b:c, 3:2)
    #  b->1, c->3, (b:c, 1:3)
    #  b->3, c->1, (b:c, 3:1)
    #  a->1, c->2, (a:c, 1:2)
    #  a->2, c->1, (a:c, 2:1)
    #  a->2, c->3, (a:c, 2:3)
    #  a->3, c->2, (a:c, 3:2)
    #  a->1, c->3, (a:c, 1:3)
    #  a->3, c->1, (a:c, 3:1)


# data = [
#         [
#             # seems good!
#             # expected mapping: earth->electrons, sun->nucleus, gravity->electricity, newton->faraday
#             # http://localhost:3000/mapping?base=earth,sun,newton,gravity&target=electrons,nucleus,electricity,faraday
#             # base=earth,sun,gravity,newton
#             # target=electrons,nucleus,electricity,faraday
#             ["earth", "sun", "gravity", "newton"], 
#             ["electrons", "nucleus", "electricity", "faraday"]
#         ],
#         [
#             # expected mapping: earth->electrons, sun->nucleus, gravity->electricity, newton->? (faraday has been removed)
#             # http://localhost:3000/mapping?base=earth,sun,newton,gravity&target=electrons,nucleus,electricity
#             # after using recursively the mapping function, it found 'humans' as the best option (instead of faraday, but maybe its not so bad?)
#             # http://localhost:3000/single-mapping?base1=gravity&base2=newton&target1=electricity&target2=humans
#             # http://localhost:3000/single-mapping?base1=gravity&base2=newton&target1=electricity&target2=faraday
#             ["earth", "sun", "gravity", "newton"], 
#             ["electrons", "nucleus", "electricity"]
#         ],
#         [
#             # http://localhost:3000/mapping?base=earth,newton,gravity&target=electrons,nucleus,electricity,faraday
#             # expected mapping: earth->electrons, gravity->electricity, newton->faraday, nucleus->? (sun has been removed)
#             # it map earth-->electricity and gravity-->electrons instead of earth-->electrons and gravity-->electricity, but their score is similar (1.833, 1.625) without IGNORE list: (2.125~1.879)
#             # http://localhost:3000/single-mapping?base1=earth&base2=gravity&target1=electricity&target2=electrons
#             # Option 1 (the chosen one): (earth-->electricity, gravity-->electrons, newton-->nucleus)
#             #   (earth:gravity, electricity:electrons): 1.833
#             #   (gravity:electrons, newton:nucleus): 0.707
#             #   total score: 2.54
#             # Option 2: (earth-->electrons, gravity-->electrivity, newton-->faraday)
#             #   (earth:gravity, electrons:electrivity): 1.625
#             #   (gravity:newton, electricity:faraday): 1
#             #   total score: 2.625
#             ["earth", "newton", "gravity"],
#             ["electrons", "nucleus", "electricity", "faraday"],
#         ],
#         [
#             # seems good!
#             # http://localhost:3000/mapping?base=thoughts,brain&target=astronaut,space
#             # expected: thoughts->astronaut, brain->space
#             ["thoughts", "brain"],
#             ["astronaut", "space"],
#         ],
#         [
#             # seems good!
#             # http://localhost:3000/mapping?base=thoughts,brain,neurons&target=astronaut,space,black%20hole
#             # expected mapping: thoughts->astronaut, brain->space, neurons->black hole
#             ["thoughts", "brain", "neurons"],
#             ["astronaut", "space", "black hole"],
#         ],
#         [
#             # seems good!
#             # http://localhost:3000/mapping?base=cars,road,wheels&target=boats,river,sail
#             # expected: cars->boats, road->river, wheels->sail
#             ["cars", "road", "wheels"],
#             ["boats", "river", "sail"],
#         ],
#         [
#             # http://localhost:3000/mapping?base=cars,road,wheels&target=boats,river
#             # expected: cars->boats, road->river, wheels->? (sail has been removed)
#             # the suggestions are not good. Need to check why sail is now suggested in "boat have .*" 
#             # why do boats .* sails --> found 'have', but why do boats have .. --> not found 'have'.
#             # maybe I should have "RelatedTo" from conceptNet: https://conceptnet.io/c/en/boat?rel=/r/RelatedTo&limit=1000
#             # well after adding quasimodo, it found streeing wheel -> sound good but I still prefer sails here..
#             ["cars", "road", "wheels"],
#             ["boats", "river"],
#         ],
#         [
#             # http://localhost:3000/mapping?base=sunscreen,sun,summer&target=umbrella,rain,winter
#             # expected: sunscreen->umbrella, sun->rain, summer->winter 
#             # the mapping is good, but the map between summer-->winter is very week!
#             # the relation between sun:summer are good, but there are no relations between rain:winter or umbrela:winter!
#             # http://localhost:3000/two-entities?entity1=rain&entity2=winter
#             ["sunscreen", "sun", "summer"],
#             ["umbrella", "rain", "winter"],
#         ],
#         [
#             # http://localhost:3000/mapping?base=student,homework,university&target=citizen,duties,country
#             # expected: student->citizen, homework->duties, university->country
#             # it found that (student:homework, citzen:country) is stronger then (student:homework, citzen:duties): 1.047 ~ 1
#             # http://localhost:3000/single-mapping?base1=student&base2=homework&target1=citizen&target2=duties
#             # http://localhost:3000/single-mapping?base1=student&base2=homework&target1=citizen&target2=country
#             # maybe few weaks relations are weaker than one stronger?
#             ["student", "homework", "university"],
#             ["citizen", "duties", "country"],
#         ],
#     ]