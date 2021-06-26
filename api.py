import os
from typing import List, Dict

import networkx as nx
from flask import Flask, jsonify, request
from networkx.algorithms import bipartite

import python2react
from utils import DISTANCE_TRESHOLDS
from sentence_embadding import SentenceEmbedding
from algorithms import get_maximum_weighted_match

app = Flask(__name__)


@app.route("/full", methods=["GET", "POST"])
def full():
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    edge1 = (request.args.get('base1'), request.args.get('base2'))
    edge2 = (request.args.get('target1'), request.args.get('target2'))

    edges_ = [
        ((edge1[0], edge1[1]),(edge2[0], edge2[1])),
        ((edge1[1], edge1[0]),(edge2[1], edge2[0])),
        ((edge1[0], edge1[1]),(edge2[1], edge2[0])),
        ((edge1[1], edge1[0]),(edge2[0], edge2[1]))
    ]
    d = {0: {}, 1: {}, 2: {}, 3: {}}

    for edge_idx, edge_ in enumerate(edges_):   
        props_edge1 = model.get_edge_props(edge_[0][0], edge_[0][1])
        props_edge2 = model.get_edge_props(edge_[1][0], edge_[1][1])
        if not props_edge1 or not props_edge2:
            for thresh in DISTANCE_TRESHOLDS:
                d[edge_idx][thresh] = {
                    "graph": {},
                    "options": {},
                    "edges_score": [],
                    "edges_equation": "",
                    "score": 0
                }
            continue

        # we want the weight of each edge between two nodes.
        similatiry_edges = [(prop1, prop2, model.similarity(prop1, prop2)) for prop1 in props_edge1 for prop2 in props_edge2]
        
        for thresh in DISTANCE_TRESHOLDS:
            clustered_sentences_1: Dict[int, List[str]] = model.clustering(edge_[0], distance_threshold=thresh)
            clustered_sentences_2: Dict[int, List[str]] = model.clustering(edge_[1], distance_threshold=thresh)

            # we want to group each cluster to one node
            nodes1 = ["\n".join(cluster) for _, cluster in clustered_sentences_1.items()]
            nodes1_for_app = python2react.get_nodes_for_app(props=nodes1, start_idx=0, x=200, group=0, promote_group=1)
            
            nodes2 = ["\n".join(cluster) for _, cluster in clustered_sentences_2.items()]
            nodes2_for_app = python2react.get_nodes_for_app(props=nodes2, start_idx=len(clustered_sentences_1), x=800, group=len(clustered_sentences_1), promote_group=1)

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
            
            # we doing this process for each threshold for the slider in the app
            d[edge_idx][thresh] = {
                "graph": {
                    "nodes": nodes1_for_app + nodes2_for_app,
                    "edges": python2react.get_edges_for_app(edges, spaces=40),
                },
                "options": python2react.get_options(len(clustered_sentences_1) + len(clustered_sentences_2)),
                "edges_score": [edge[2] for edge in edges],
                "edges_equation": "+".join([f'edge{i}' for i in range(len(edges))]),
                "score": round(sum([edge[2] for edge in edges]), 3)
            }
    return jsonify(d)


@app.route("/bipartite", methods=["GET", "POST"])
def bipartite_graph():
    edge1 = (request.args.get('base1'), request.args.get('base2'))
    edge2 = (request.args.get('target1'), request.args.get('target2'))
    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    props_edge1 = model.get_edge_props(edge1[0], edge1[1])
    props_edge2 = model.get_edge_props(edge2[0], edge2[1])

    props1 = python2react.get_nodes_for_app(props=props_edge1, start_idx=0, x=200, group=0)
    props2 = python2react.get_nodes_for_app(props=props_edge2, start_idx=len(props1), x=800, group=1)
    
    similatiry_edges = get_maximum_weighted_match(model, props_edge1, props_edge2)

    return jsonify({
        "nodes": props1 + props2,
        "edges": python2react.get_edges_for_app(similatiry_edges),
    })


@app.route("/cluster", methods=["GET", "POST"])
def clustring():
    edge1 = (request.args.get('base1'), request.args.get('base2'))
    edge2 = (request.args.get('target1'), request.args.get('target2'))

    model = SentenceEmbedding(init_quasimodo=False, init_inflect=False)

    d = {}
    for thresh in DISTANCE_TRESHOLDS:
        clustered_sentences_1: Dict[int, List[str]] = model.clustering(edge1, distance_threshold=thresh)
        nodes1 = python2react.get_cluster_nodes_for_app(clustered_sentences_1, start_idx=0, start_gourp=0, x=200)

        clustered_sentences_2: Dict[int, List[str]] = model.clustering(edge2, distance_threshold=thresh)
        nodes2 = python2react.get_cluster_nodes_for_app(clustered_sentences_2, start_idx=nodes1.get("total_nodes"), start_gourp=len(clustered_sentences_1), x=800)

        d[thresh] = {
            "graph": {
                "nodes": nodes1.get("nodes") + nodes2.get("nodes"),
                "edges": [],
            },
            "options": python2react.get_options(len(clustered_sentences_1) + len(clustered_sentences_2)),
        }

    return jsonify(d)


if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    app.run('localhost', port=5000, debug=True)