# import json

# import requests

# # payload = {'query': 'why does earth'}
# payload = {'variables': 'query'}
# url = f"https://www.quora.com/graphql/gql_para_POST?q=SiteSearchBarQuery"
# r = requests.post(url, json=json.dumps(payload))
# print(r.text)
# # suggestions = json.loads(r.text)[1]

import os
import random
from itertools import combinations
from typing import List, Dict, Tuple

from tqdm import tqdm
import networkx as nx
from networkx.algorithms import bipartite

from sentence_embadding import SentenceEmbedding


# DISTANCE_TRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
DISTANCE_TRESHOLDS = [0.8]


def get_edges_weights(model: SentenceEmbedding, props_edge1: List[str], props_edge2: List[str]):
    # get all edges in the graph (full graph)
    return [(prop1, prop2, model.similarity(prop1, prop2)) for prop1 in props_edge1 for prop2 in props_edge2]


def get_maximum_weighted_match(model: SentenceEmbedding, props_edge1: List[str], props_edge2: List[str], return_names: bool = False):
    B = nx.Graph()
    B.add_nodes_from(list(range(len(props_edge1))), bipartite=0)
    B.add_nodes_from(list(range(len(props_edge1), len(props_edge1) + len(props_edge2))), bipartite=1)
    all_edges = {}

    for i, prop1 in enumerate(props_edge1):
        for j, prop2 in enumerate(props_edge2):
            similatiry = model.similarity(prop1, prop2)
            B.add_edge(i, len(props_edge1) + j, weight=max(0, 1-similatiry))
            all_edges[(i, len(props_edge1) + j)] = similatiry

    best_matching = bipartite.matching.minimum_weight_full_matching(B, weight='weight')
    similatiry_edges = []
    already_seen = set()
    for head, tail in best_matching.items():
        if (head, tail) not in already_seen and (tail, head) not in already_seen:
            similatiry_edges.append((head, tail, all_edges[(head, tail)]))
            already_seen.add((head, tail))

    if return_names:
        return [(
            props_edge1[edge[0]], 
            props_edge2[edge[1] - len(props_edge1)], 
            edge[2]) 
            for edge in similatiry_edges]
    return similatiry_edges


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


def update_paris_map(pairs_map, base_already_mapping, target_already_mapping):
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


def update_list(already_mapping_list, entities):
    if entities[0] not in already_mapping_list:
        already_mapping_list.append(entities[0])
    if entities[1] not in already_mapping_list:
        already_mapping_list.append(entities[1])
    return already_mapping_list


def get_best_pair_mapping(model, available_maps, base_already_mapping, target_already_mapping):
    mappings = []

    # we will iterate over all the possible pairs mapping ((n choose 2)*(n choose 2)*2), 2->2, 3->18, 4->72
    for mapping in tqdm(available_maps):
        # for each mapping we want both direction, for example:
        # if we have in the base: earth, sun. AND in the target: electrons, nucleus.
        # for the mapping earth->electrons, sun->nucleus , we will calculate: 
        # earth .* sun, electrons .* nucleus AND sun .* earth, nucleus .* electrons
        mapping_score = 0
        for direction in mapping:
            props_edge1 = model.get_edge_props(direction[0][0], direction[0][1])
            props_edge2 = model.get_edge_props(direction[1][0], direction[1][1])

            if not props_edge1 or not props_edge2:
                continue

            # we want the weight of each edge between two nodes.
            similatiry_edges = get_edges_weights(model, props_edge1, props_edge2)
    
            clustered_sentences_1: Dict[int, List[str]] = model.clustering(direction[0], distance_threshold=0.8)
            clustered_sentences_2: Dict[int, List[str]] = model.clustering(direction[1], distance_threshold=0.8)

            # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
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
                
            # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
            B = nx.Graph()
            B.add_nodes_from(list(range(len(clustered_sentences_1))), bipartite=0)
            B.add_nodes_from(list(range(len(clustered_sentences_1), len(clustered_sentences_1) + len(clustered_sentences_2))), bipartite=1)
            all_edges = {}

            for i in range(len(clustered_sentences_1)):
                for j in range(len(clustered_sentences_2)):
                    if (i, len(clustered_sentences_1) + j) not in cluster_edges_weights:
                        continue
                    similatiry = cluster_edges_weights[(i, len(clustered_sentences_1) + j)][2]
                    B.add_edge(i, len(clustered_sentences_1) + j, weight=max(0, 1-similatiry))
                    all_edges[(i, len(clustered_sentences_1) + j)] = similatiry

            best_matching = bipartite.matching.minimum_weight_full_matching(B, weight='weight')
            edges = []
            already_seen = set()
            for head, tail in best_matching.items():
                if (head, tail) not in already_seen and (tail, head) not in already_seen:
                    edges.append((head, tail, all_edges[(head, tail)]))
                    already_seen.add((head, tail))
            
            mapping_score += round(sum([edge[2] for edge in edges]), 3)

        mappings.append((mapping[0], mapping_score))

    mappings = sorted(mappings, key=lambda x: x[1], reverse=True)
    return {
        "best_mapping": mappings[0][0],
        "best_score": mappings[0][1],
        "base_already_mapping": update_list(base_already_mapping, [mappings[0][0][0][0], mappings[0][0][0][1]]),
        "target_already_mapping": update_list(target_already_mapping, [mappings[0][0][1][0], mappings[0][0][1][1]])
    }


def mapping(base, target):
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)
    base_already_mapping = []
    target_already_mapping = []
    
    all_possible_pairs_map: List[List[List[Tuple[str, str]]]] = get_all_possible_pairs_map(base, target)
    while len(base_already_mapping) != len(base):
        all_possible_pairs_map = update_paris_map(all_possible_pairs_map, base_already_mapping, target_already_mapping)
        res = get_best_pair_mapping(model, all_possible_pairs_map, base_already_mapping, target_already_mapping)
        base_already_mapping = res["base_already_mapping"]
        target_already_mapping = res["target_already_mapping"]

    return [f"{b} --> {t}" for b, t in zip(base_already_mapping, target_already_mapping)]


if __name__ == "__main__":
    base = ["earth", "sun", "gravity", "newton"]
    target = ["electrons", "nucleus", "electricity", "faraday"]
    res = mapping(base, target)
    print(res)

    # res = get_all_possible_pairs_map(["earth", "sun", "gravity"], ["electrons", "nucleus", "electricity"])
    # for entry in res:
    #     print(entry)

