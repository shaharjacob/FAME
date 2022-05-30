import json
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional

import networkx as nx
from click import secho
from networkx.algorithms import bipartite

from utils.sentence_embadding import SentenceEmbedding


COLORS_BRIGHT = [
    # https://www.w3schools.com/cssref/css_colors.asp
    "#7fffd4", # Aquamarine
    "#7fff00", # Chartreuse
    "#ffa07a", # LightSalmon
    "#00ffff", # Cyan
    "#ffb6c1", # LightPink
    "#ffd700", # Gold
    "#ffa500", # Orange
]


COLORS_DARK = [
    "#0000ff", # Blue
    "#8a2be2", # BlueViolet
    "#a52a2a", # Brown
    "#008000", # Green
    "#dc143c", # Crimson
    "#4b0082", # Indigo
]


# DISTANCE_TRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
DISTANCE_TRESHOLDS = [0.5]

def get_int(val: Optional[int], default_value: int) -> int:
    try:
        arg = int(val)
    except:
        arg = default_value
    return arg


def get_spaces(i, n):
    return " ".join([""]*n)


def get_edges_combinations(edge1: Tuple[str, str], edge2: Tuple[str, str]):
    return [
        ((edge1[0], edge1[1]),(edge2[0], edge2[1])),
        ((edge1[1], edge1[0]),(edge2[1], edge2[0])),
        ((edge1[0], edge1[1]),(edge2[1], edge2[0])),
        ((edge1[1], edge1[0]),(edge2[0], edge2[1]))
    ]


def get_ordered_edges_similarity(model: SentenceEmbedding, cluster1: List[str], cluster2: List[str]):
    edges = []
    for edge1 in cluster1:
        for edge2 in cluster2:
            edges.append((edge1, edge2, model.similarity(edge1, edge2)))
    return sorted(edges, key=lambda x: x[2], reverse=True)


def read_json(path: Union[str, Path]) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def get_edge_score(prop1: str, prop2: str, model: SentenceEmbedding, freq) -> float:
    if prop1 in freq.stopwords or prop2 in freq.stopwords:
        return 0
    else:
        return model.similarity(prop1, prop2)


def get_maximum_weighted_match(model: SentenceEmbedding, 
                            props_edge1: Union[List[str], Dict[int, List[str]]],
                            props_edge2: Union[List[str], Dict[int, List[str]]], 
                            weights: Dict[Tuple[int, int], Tuple[str, str, float]] = None,
                            freq=None
                            ) -> List[Tuple[str, str, float]]:
    if isinstance(props_edge1, Dict) or isinstance(props_edge2, Dict):
        # means that this is a clusters mode. So we need the weights that we already calculated
        if not weights:
            secho("[ERROR] in clusters mode, weights has two calculated before", fg="red", bold=True)
            exit(1)

    B = nx.Graph()
    B.add_nodes_from(list(range(len(props_edge1))), bipartite=0)
    B.add_nodes_from(list(range(len(props_edge1), len(props_edge1) + len(props_edge2))), bipartite=1)

    all_edges = {}
    for i, prop1 in enumerate(props_edge1):
        for j, prop2 in enumerate(props_edge2):
            if weights:
                if (i, len(props_edge1) + j) not in weights:
                    continue
                similatiry = weights[(i, len(props_edge1) + j)][2]
            else:
                similatiry = get_edge_score(prop1, prop2, model, freq)
            B.add_edge(i, len(props_edge1) + j, weight=max(0, 1-similatiry))
            all_edges[(i, len(props_edge1) + j)] = similatiry

    best_matching = bipartite.matching.minimum_weight_full_matching(B, weight='weight')
    similatiry_edges = []
    already_seen = set()
    for head, tail in best_matching.items():
        if (head, tail) not in already_seen and (tail, head) not in already_seen:
            similatiry_edges.append((head, tail, all_edges[(head, tail)]))
            already_seen.add((head, tail))

    return similatiry_edges


def is_none(val):
    if not val:
        return True
    if val == 'None' or val == 'none':
        return True
    return False
