import os
import random
from typing import List, Dict

import networkx as nx
from flask import Flask, jsonify, request
from networkx.algorithms import bipartite

from utils import COLORS_BRIGHT
from sentence_embadding import SentenceEmbedding

app = Flask(__name__)


def get_spaces(i, n):
    return " ".join([""]*n)


def get_edges_for_app(edges: List[str], spaces: int = 80) -> List[Dict]:
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
            "label": f"{get_spaces(i, random.randint(0, spaces))}{str(edge[2])}",
            "value": edge[2],
            "width": 0.5,
            "arrows": {
                "from": { "enabled": False },
                "to": { "enabled": False },
            },
        } 
        for i, edge in enumerate(edges)]


def get_nodes_for_app(props: List[str], start_idx: int, x: int, group: str, promote_group: int = 0) -> List[Dict]:
    nodes = []
    curr_y = 0
    for i, node in enumerate(props):
        print(curr_y)
        nodes.append({
            "id": i + start_idx, 
            "x": x,
            "y": curr_y,
            "label": node, 
            "group": str(group + (promote_group*i)),
            "font": "12px arial #343434"
        })
        curr_y += len(node.split('\n'))*40
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


def remove_edges_from_same_clusters(edges: List[tuple], nodes1: dict, nodes2: dict) -> List[tuple]:
    clusters_edges = {}
    for edge in edges:
        cluster1, cluster2 = None, None
        for node in nodes1:
            if node.get("id") == edge[0]:
                cluster1 = node.get("group")
                break
        for node in nodes2:
            if node.get("id") == edge[1]:
                cluster2 = node.get("group")
                break

        if (cluster1, cluster2) not in clusters_edges:
            clusters_edges[(cluster1, cluster2)] = edge
        else:
            if edge[2] > clusters_edges[(cluster1, cluster2)][2]:
                clusters_edges[(cluster1, cluster2)] = edge
    return [v for k, v in clusters_edges.items()]


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


def get_edges_weighted(model: SentenceEmbedding, props_edge1: List[str], props_edge2: List[str]):
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


@app.route("/api", methods=["GET", "POST"])
def bipartite_graph():
    edge1 = (request.args.get('head1'), request.args.get('tail1'))
    edge2 = (request.args.get('head2'), request.args.get('tail2'))
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    props_edge1 = model.get_edge_props(edge1[0], edge1[1])
    props_edge2 = model.get_edge_props(edge2[0], edge2[1])

    props1 = get_nodes_for_app(props=props_edge1, start_idx=0, x=200, group="0")
    props2 = get_nodes_for_app(props=props_edge2, start_idx=len(props1), x=800, group="1")
    
    similatiry_edges = get_maximum_weighted_match(model, props_edge1, props_edge2)

    return jsonify({
        "nodes": props1 + props2,
        "edges": get_edges_for_app(similatiry_edges),
    })


@app.route("/test", methods=["GET", "POST"])
def test():
    edge1 = (request.args.get('head1'), request.args.get('tail1'))
    edge2 = (request.args.get('head2'), request.args.get('tail2'))

    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    props_edge1 = model.get_edge_props(edge1[0], edge1[1])
    props_edge2 = model.get_edge_props(edge2[0], edge2[1])
    similatiry_edges = get_edges_weighted(model, props_edge1, props_edge2)

    d = {}
    distance_thresholds = [0.8]
    for thresh in distance_thresholds:

        clustered_sentences_1: Dict[int, List[str]] = model.clustering(edge1, distance_threshold=thresh)
        clustered_sentences_1 = dict(sorted(clustered_sentences_1.items()))

        clustered_sentences_2: Dict[int, List[str]] = model.clustering(edge2, distance_threshold=thresh)
        clustered_sentences_2 = dict(sorted(clustered_sentences_2.items()))

        props = []
        cluster1 = []
        for _, cluster in clustered_sentences_1.items():
            cluster1.append("\n".join(cluster))
        props.extend(get_nodes_for_app(props=cluster1, start_idx=0, x=200, group=0, promote_group=1))
        
        cluster2 = []
        for _, cluster in clustered_sentences_2.items():
            cluster2.append("\n".join(cluster))
        props.extend(get_nodes_for_app(props=cluster2, start_idx=len(clustered_sentences_1), x=800, group=len(clustered_sentences_1), promote_group=1))
        
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
        similatiry_edges = []
        already_seen = set()
        for head, tail in best_matching.items():
            if (head, tail) not in already_seen and (tail, head) not in already_seen:
                similatiry_edges.append((head, tail, all_edges[(head, tail)]))
                already_seen.add((head, tail))
        
        d[thresh] = {
            "graph": {
                "nodes": props,
                "edges": get_edges_for_app(similatiry_edges, spaces=40),
            },
            "options": get_options(len(clustered_sentences_1) + len(clustered_sentences_2)),
        }

    return jsonify(d)


@app.route("/cluster", methods=["GET", "POST"])
def clustring():
    d = {}
    edge1 = (request.args.get('head1'), request.args.get('tail1'))
    edge2 = (request.args.get('head2'), request.args.get('tail2'))
    calc_edges = request.args.get('edges')
    between_clusters = request.args.get('clusters')
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    distance_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for thresh in distance_thresholds:
        clustered_sentences_1: Dict[int, List[str]] = model.clustering(edge1, distance_threshold=thresh)
        nodes1 = get_cluster_nodes_for_app(clustered_sentences_1, start_idx=0, start_gourp=0, x=200)

        clustered_sentences_2: Dict[int, List[str]] = model.clustering(edge2, distance_threshold=thresh)
        nodes2 = get_cluster_nodes_for_app(clustered_sentences_2, start_idx=nodes1.get("total_nodes"), start_gourp=len(clustered_sentences_1), x=800)
        
        edges = []
        if calc_edges == 'true':
            props1 = [node.get("label") for node in nodes1.get("nodes")]
            props2 = [node.get("label") for node in nodes2.get("nodes")]
            edges = get_maximum_weighted_match(model, props1, props2)

            if between_clusters == 'true':
                edges = remove_edges_from_same_clusters(edges, nodes1.get("nodes"), nodes2.get("nodes"))
                _nodes1, _nodes2 = [], []
                for edge in edges:
                    for node in nodes1.get("nodes"):
                        if node.get("id") == edge[0]:
                            _nodes1.append(node.get("label"))
                            break
                    for node in nodes2.get("nodes"):
                        if node.get("id") == edge[1]:
                            _nodes2.append(node.get("label"))
                            break        
                edges = get_maximum_weighted_match(model, _nodes1, _nodes2, return_names=True)
                for i in range(len(edges)):
                    for node in nodes1.get("nodes"):
                        if node["label"] == edges[i][0]:
                            edges[i] = (node["id"], edges[i][1], edges[i][2])
                            break
                    for node in nodes2.get("nodes"):
                        if node["label"] == edges[i][1]:
                            edges[i] = (edges[i][0], node["id"], edges[i][2])
                            break
                
            edges = get_edges_for_app(edges)

        d[thresh] = {
            "graph": {
                "nodes": nodes1.get("nodes") + nodes2.get("nodes"),
                "edges": edges,
            },
            "options": get_options(len(clustered_sentences_1) + len(clustered_sentences_2)),
        }

    return jsonify(d)


if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    app.run('localhost', port=5000, debug=True)