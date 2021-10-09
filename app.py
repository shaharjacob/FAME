import os
import time
from typing import List, Dict

from flask import Flask, jsonify, request

import utils
import mapping
import python2react
from frequency import Frequencies
from data_collector import DataCollector
from sentence_embadding import SentenceEmbedding

app = Flask(__name__)

@app.route("/mapping", methods=["GET", "POST"])
def mapping_entities():
    start_time = time.time()
    data_collector = DataCollector()
    model_name = 'msmarco-distilbert-base-v4'
    model = SentenceEmbedding(model=model_name, data_collector=data_collector)
    threshold = request.args.get('threshold')
    threshold = threshold if threshold else mapping.FREQUENCY_THRESHOLD
    freq_json_folder = 'jsons/merged/20%'
    freq = Frequencies(f'{freq_json_folder}/all_1m_filter_3_sort.json', threshold=float(threshold))
    base = [b.strip() for b in request.args.get('base').split(',')]
    target = [t.strip() for t in request.args.get('target').split(',')]
    depth = utils.get_int(request.args.get('depth'), 4)
    top_n = utils.get_int(request.args.get('top'), 3)
    num_of_suggestions = utils.get_int(request.args.get('suggestions'), 3)
    data = []
    scores = []
    
    # here we map between base entitites and target entities
    solutions = mapping.mapping_wrapper(
                                    base=base, 
                                    target=target, 
                                    suggestions=True, 
                                    depth=depth, 
                                    top_n=top_n, 
                                    num_of_suggestions=num_of_suggestions, 
                                    freq=freq, 
                                    model_name=model_name, 
                                    threshold=float(threshold)
                                )

    for solution in solutions:
        # prepare the nodes for the react app
        nodes = python2react.get_nodes_for_app(props=solution.mapping, start_idx=0)
        nodes_val2index = {node:i for i, node in enumerate(solution.mapping)}
        edges = []
        max_score_for_scaling = 0

        # we iterate over the mapping that found. 
        # the first iterate is the strongest map, and so on.
        for relation in solution.relations:
            # we count both direction. for example earth:sun, electrons:nucleus, we want also sun:earth, nucleus:electrons.
            for direction in range(2):
                node1 = f"{relation[0][0]} --> {relation[1][0]}"
                node2 = f"{relation[0][1]} --> {relation[1][1]}"
                edge = (nodes_val2index[node1], nodes_val2index[node2])
                if direction == 1:
                    edge = (edge[1], edge[0])
                    relation = [(relation[0][1], relation[0][0]), (relation[1][1], relation[1][0])]

                # now we extract information of the relation. 
                # actually we already did it in mapping.mapping_wrapper(base, target), but this is very quick since we already saved all the props.
                # and it more readable to do it here again.
                graph = mapping.get_pair_mapping(model, data_collector, freq, relation)
                if not graph:
                    continue

                # now we are building the labels on the edge between two nodes (node is a map between base and target)
                # we take the best prop in each cluster.
                label = []
                for i, cluster_edge in enumerate(graph["graph"]):
                    props = utils.get_ordered_edges_similarity(model, graph["clusters1"][cluster_edge[0]], graph["clusters2"][cluster_edge[1] - len(graph["clusters1"])])
                    label.append(f"{relation[0][0]} {props[0][0]} {relation[0][1]} :: {relation[1][0]} {props[0][1]} {relation[1][1]} :: {cluster_edge[2]}")
                label = sorted(label, key=lambda x: x.split('::')[2], reverse=True)[:mapping.NUM_OF_CLUSTERS_TO_CALC]
                label = [l for l in label if float(l.split('::')[2]) > mapping.EDGE_THRESHOLD]
                edges.append(python2react.get_single_edge_for_app(edge, "\n".join(label), graph["score"], len(edges)))
                max_score_for_scaling = max(max_score_for_scaling, graph["score"])

        # for scaling
        for edge in edges:
            edge["scaling"]["max"] = max_score_for_scaling
        
        data.append({
            "graph": {
                    "nodes": nodes,
                    "edges": edges,
                },
            "top_suggestions" : solution.top_suggestions
        })
        
        scores.append({
            "label": f"Top #{len(scores)+1} ({solution.score})",
            "value": len(scores)
        })

    return jsonify({
        "data": data,
        "scores": scores,
        "time": round(time.time() - start_time, 2),
    })


@app.route("/single-mapping", methods=["GET", "POST"])
def single_mapping():
    data_collector = DataCollector()
    model = SentenceEmbedding(model='msmarco-distilbert-base-v4', data_collector=data_collector)

    edge1 = (request.args.get('base1'), request.args.get('base2'))
    edge2 = (request.args.get('target1'), request.args.get('target2'))
    d = {0: {}, 1: {}, 2: {}, 3: {}}
    
    threshold = request.args.get('threshold')
    threshold = threshold if threshold else mapping.FREQUENCY_THRESHOLD
    freq_json_folder = 'jsons/merged/20%'
    freq = Frequencies(f'{freq_json_folder}/all_1m_filter_3_sort.json', threshold=float(threshold))

    for edge_idx, edge_ in enumerate(utils.get_edges_combinations(edge1, edge2)):   
        props_edge1 = data_collector.get_entities_relations(edge_[0][0], edge_[0][1])
        props_edge2 = data_collector.get_entities_relations(edge_[1][0], edge_[1][1])
        if not props_edge1 or not props_edge2:
            for thresh in utils.DISTANCE_TRESHOLDS:
                d[edge_idx][thresh] = {
                    "graph": {},
                    "options": {},
                    "score": 0
                }
            continue

        # we want the weight of each edge between two nodes.
        similatiry_edges = [(prop1, prop2, mapping.get_edge_score(prop1, prop2, model, freq)) for prop1 in props_edge1 for prop2 in props_edge2]
        
        for thresh in utils.DISTANCE_TRESHOLDS:
            clustered_sentences_1: Dict[int, List[str]] = model.clustering(edge_[0], distance_threshold=thresh)
            clustered_sentences_2: Dict[int, List[str]] = model.clustering(edge_[1], distance_threshold=thresh)

            # we want to group each cluster to one node
            nodes1 = ["\n".join(cluster) for _, cluster in clustered_sentences_1.items()]
            nodes1_for_app = python2react.get_nodes_for_app_bipartite(props=nodes1, start_idx=0, x=200, group=0, promote_group=1)
            
            nodes2 = ["\n".join(cluster) for _, cluster in clustered_sentences_2.items()]
            nodes2_for_app = python2react.get_nodes_for_app_bipartite(props=nodes2, start_idx=len(clustered_sentences_1), x=800, group=len(clustered_sentences_1), promote_group=1)

            # for each two clusters (from the opposite side of the bipartite) we will take only one edge, which is the maximum weighted.
            cluster_edges_weights = mapping.get_edges_with_maximum_weight(similatiry_edges, clustered_sentences_1, clustered_sentences_2)
                
            # now we want to get the maximum weighted match, which hold the constraint that each cluster has no more than one edge.
            edges = utils.get_maximum_weighted_match(model, clustered_sentences_1, clustered_sentences_2, weights=cluster_edges_weights)
            edges = sorted(edges, key=lambda x: x[2], reverse=True)
            
            # we doing this process for each threshold for the slider in the app
            d[edge_idx][thresh] = {
                "graph": {
                    "nodes": nodes1_for_app + nodes2_for_app,
                    "edges": python2react.get_edges_for_app(edges, spaces=40),
                },
                "options": python2react.get_options(len(clustered_sentences_1) + len(clustered_sentences_2)),
                "score": round(sum([edge[2] for edge in edges[:mapping.NUM_OF_CLUSTERS_TO_CALC] if edge[2] > mapping.EDGE_THRESHOLD]), 3)
            }
    return jsonify(d)


@app.route("/two-entities", methods=["GET", "POST"])
def two_entities():
    entity1 = request.args.get('entity1') 
    entity2 = request.args.get('entity2')
    data_collector = DataCollector() 

    props1 = data_collector.get_entities_relations(entity1, entity2, from_where=True)
    for k, v in props1.items():
        props1[k] = "<br/>".join(v)

    props2 = data_collector.get_entities_relations(entity2, entity1, from_where=True)
    for k, v in props2.items():
        props2[k] = "<br/>".join(v)

    return jsonify({
        f"{entity1} .* {entity2}": props1, 
        f"{entity2} .* {entity1}": props2
    })


@app.route("/bipartite", methods=["GET", "POST"])
def bipartite_graph():
    base1 = request.args.get('base1')
    base2 = request.args.get('base2')
    target1 = request.args.get('target1')
    target2 = request.args.get('target2')

    data_collector = DataCollector()
    model = SentenceEmbedding(data_collector=data_collector)
    threshold = request.args.get('threshold')
    threshold = threshold if threshold else mapping.FREQUENCY_THRESHOLD
    freq_json_folder = 'jsons/merged/20%'
    freq = Frequencies(f'{freq_json_folder}/all_1m_filter_3_sort.json', threshold=float(threshold))

    if not utils.is_none(base1) and not utils.is_none(base2) and not utils.is_none(target1) and not utils.is_none(target2):
        props_edge1 = data_collector.get_entities_relations(base1, base2)
        props_edge2 = data_collector.get_entities_relations(target1, target2)
    else:
        props_edge1 = request.args.get('left').split(",")
        props_edge2 = request.args.get('right').split(",")
        
    props1 = python2react.get_nodes_for_app_bipartite(props=props_edge1, start_idx=0, x=200, group=0)
    props2 = python2react.get_nodes_for_app_bipartite(props=props_edge2, start_idx=len(props1), x=800, group=1)
    
    similatiry_edges = utils.get_maximum_weighted_match(model, props_edge1, props_edge2, freq=freq)

    return jsonify({
        "nodes": props1 + props2,
        "edges": python2react.get_edges_for_app(similatiry_edges),
    })


@app.route("/cluster", methods=["GET", "POST"])
def clustring():
    edge1 = (request.args.get('base1'), request.args.get('base2'))
    edge2 = (request.args.get('target1'), request.args.get('target2'))

    data_collector = DataCollector()
    model = SentenceEmbedding(data_collector=data_collector)

    d = {}
    for thresh in utils.DISTANCE_TRESHOLDS:
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
    app.run('localhost', port=5000, debug=False)