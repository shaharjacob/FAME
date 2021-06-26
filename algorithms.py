from typing import List, Dict, Tuple

import networkx as nx
from networkx.algorithms import bipartite

from sentence_embadding import SentenceEmbedding


def get_maximum_weighted_match(model: SentenceEmbedding, 
                            props_edge1: List[str], 
                            props_edge2: List[str], 
                            weights: Dict[Tuple[int, int], Tuple[str, str, float]] = None
                            ) -> List[Tuple[str, str, float]]:
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

    return similatiry_edges
