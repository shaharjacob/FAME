import random
from typing import List, Dict, Tuple

from utils import utils


def get_edges_for_app(edges: List[str], spaces: int = 80) -> List[Dict]:
    return [
        {
            "id": f"{edge[0]}:{edge[1]}",
            "from": edge[0], 
            "to": edge[1], 
            "scaling": {
                "min": 0.01,
                "max": 1,
                "label": {
                    "enabled": True,
                    "min": 8,
                    "max": 20,
                },
            },
            "font": {
                "align": 'left',
            },
            "label": f"{utils.get_spaces(i, random.randint(0, spaces))}{str(edge[2])}",
            "value": edge[2],
            "width": 0.5,
            "arrows": {
                "from": { "enabled": False },
                "to": { "enabled": False },
            },
        } 
        for i, edge in enumerate(edges)]


def get_single_edge_for_app(edge: Tuple[str, str], label: str, value: float, count: int) -> dict:
    return {
            "id": f"{edge[0]}:{edge[1]}",
            "from": edge[0], 
            "to": edge[1], 
            "scaling": {
                "min": 0.01,
                "max": 1,
                "label": {
                    "enabled": True,
                    "min": 6,
                    "max": 8,
                },
            },
            "font": {
                "color": utils.COLORS_DARK[count % len(utils.COLORS_DARK)],
                "face": "arial",
                "align": 'left',
            },
            "label": label,
            "value": value,
            "width": 0.5,
            "smooth": {
                "enabled": True,
                "type": "curvedCW",
                "roundness": 0.3,
            },
            "arrows": {
                "from": { "enabled": False },
                "to": { "enabled": True },
            },
        }


def get_nodes_for_app(props: List[str], start_idx: int) -> List[Dict]:
    nodes = []
    for i, node in enumerate(props):
        nodes.append({
            "id": i + start_idx, 
            "x": i * 250,
            "y": i,
            "label": node, 
            "font": "12px arial #343434"
        })
    return nodes


def get_nodes_for_app_bipartite(props: List[str], start_idx: int, x: int, group: int, promote_group: int = 0) -> List[Dict]:
    nodes = []
    curr_y = 0
    for i, node in enumerate(props):
        nodes.append({
            "id": i + start_idx, 
            "x": x,
            "y": curr_y,
            "label": node, 
            "group": str(group + (promote_group*i)),
            "font": "12px arial #343434"
        })
        curr_y += max(1, len(node.split('\n'))) * 40
    return nodes


def get_cluster_nodes_for_app(clustered_sentences: Dict[int, List[str]], start_idx: int, start_gourp: int, x: int) -> List[Dict]:
    nodes = []
    total_nodes = 0
    cluster_count = 0
    for i, cluster in clustered_sentences.items():
        for j, prop in enumerate(cluster):
            nodes.append({
                "id": total_nodes + start_idx, 
                "x": x,
                "y": (total_nodes * 35) + (cluster_count * 10),
                "label": prop, 
                "group": int(i) + start_gourp,
                "font": "16px arial #343434",
                "margin": 8,
            })
            total_nodes += 1
        cluster_count += 1
    return {
        "nodes": nodes,
        "total_nodes": total_nodes,
    }


def get_options(num_of_clusters: int):
    groups = {}
    for i in range(num_of_clusters):
        groups[i] = {
            "color": {
                "background": utils.COLORS_BRIGHT[i % len(utils.COLORS_BRIGHT)],
                "border": "#343434",
            },
            "borderWidth": 0.5,
        }

    return {
        "physics": {
            "enabled": False,
        },
        "height": "800px",
        "groups": groups,
    }