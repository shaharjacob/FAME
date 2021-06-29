from typing import Tuple, List

from sentence_embadding import SentenceEmbedding

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
    "#dc143c", # Crimson
    "#4b0082", # Indigo
    "#008000", # Green
]


# DISTANCE_TRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
DISTANCE_TRESHOLDS = [0.8]


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
