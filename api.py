import os
import random
from typing import List, Dict, Tuple

import networkx as nx
from flask import Flask, jsonify, request
from networkx.algorithms import bipartite
from scipy.spatial import distance

from utils import COLORS_BRIGHT
from sentence_embadding import SentenceEmbedding

app = Flask(__name__)


def get_spaces(i, n):
    return " ".join([""]*n)


def get_edges_for_app(edges: List[str]) -> List[Dict]:
    return [
        {
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
            "label": f"{get_spaces(i, random.randint(0, 40))}{str(edge[2])}",
            "value": edge[2],
            "width": 0.5,
            "arrows": {
                "from": { "enabled": False },
                "to": { "enabled": False },
            },
        } 
        for i, edge in enumerate(edges)]


def get_nodes_for_app(props: List[str], start_idx: int, x: int, group: str) -> List[Dict]:
    return [
        {
            "id": i + start_idx, 
            "x": x,
            "y": i*38,
            "label": node, 
            "group": group,
            "font": "12px arial #343434"
        } 
        for i, node in enumerate(props)]


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
                "background": COLORS_BRIGHT[i % len(COLORS_BRIGHT)],
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


def get_maximum_weighted_match(model: SentenceEmbedding, props_edge1: List[str], props_edge2: List[str]):
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

    return similatiry_edges


def get_trivial_match(model: SentenceEmbedding, props_edge1: List[str], props_edge2: List[str]) -> List[Tuple]:
    similatiry_edges = []
    for i, prop1 in enumerate(props_edge1):
        max_score = 0
        best_edge = ()
        for j, prop2 in enumerate(props_edge2):
            similatiry = model.similarity(prop1, prop2)
            if similatiry > max_score:
                max_score = similatiry
                best_edge = (i, len(props_edge1) + j)
        if max_score > 0:
            similatiry_edges.append((best_edge[0], best_edge[1], max_score))
    return similatiry_edges


@app.route("/api", methods=["GET", "POST"])
def bipartite_graph():
    edge1 = (request.args.get('head1'), request.args.get('tail1'))
    edge2 = (request.args.get('head2'), request.args.get('tail2'))
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    props_edge1 = model.get_edge_props(edge1[0], edge1[1])
    props_edge2 = model.get_edge_props(edge2[0], edge2[1])

    props1 = get_nodes_for_app(props=props_edge1, start_idx=0, x=200, group="0")
    props2 = get_nodes_for_app(props=props_edge2, start_idx=len(props1), x=800, group="1")
    
    # similatiry_edges = get_trivial_match(model, props_edge1, props_edge2)
    similatiry_edges = get_maximum_weighted_match(model, props_edge1, props_edge2)

    return jsonify({
        "nodes": props1 + props2,
        "edges": get_edges_for_app(similatiry_edges),
    })


@app.route("/cluster", methods=["GET", "POST"])
def clustring():
    d = {}
    edge1 = (request.args.get('head1'), request.args.get('tail1'))
    edge2 = (request.args.get('head2'), request.args.get('tail2'))
    calc_edges = request.args.get('edges')
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    distance_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for thresh in distance_thresholds:
        clustered_sentences_1 = model.clustering(edge1, distance_threshold=thresh)
        nodes1 = get_cluster_nodes_for_app(clustered_sentences_1.get("clustered_sentences"), start_idx=0, start_gourp=0, x=200)

        clustered_sentences_2 = model.clustering(edge2, distance_threshold=thresh)
        nodes2 = get_cluster_nodes_for_app(clustered_sentences_2.get("clustered_sentences"), start_idx=nodes1.get("total_nodes"), start_gourp=len(clustered_sentences_1), x=800)
        
        edges = []
        if calc_edges == 'true':
            edges = get_maximum_weighted_match(model, clustered_sentences_1.get("props"), clustered_sentences_2.get("props"))
            edges = get_edges_for_app(edges)

        d[thresh] = {
            "graph": {
                "nodes": nodes1.get("nodes") + nodes2.get("nodes"),
                "edges": edges,
            },
            "options": get_options(len(clustered_sentences_1.get("clustered_sentences")) + len(clustered_sentences_2.get("clustered_sentences"))),
        }

    return jsonify(d)


if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    app.run('localhost', port=5000, debug=True)