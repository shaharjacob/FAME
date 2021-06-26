from typing import List, Dict, Tuple, Union

import networkx as nx
from click import secho
from networkx.algorithms import bipartite

from sentence_embadding import SentenceEmbedding


def get_maximum_weighted_match(model: SentenceEmbedding, 
                            props_edge1: Union[List[str], Dict[int, List[str]]],
                            props_edge2: Union[List[str], Dict[int, List[str]]], 
                            weights: Dict[Tuple[int, int], Tuple[str, str, float]] = None
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
