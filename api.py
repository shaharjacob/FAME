from typing import List, Dict

from flask import Flask, jsonify

from sentence_embadding import SentenceEmbedding

# export FLASK_ENV=development

app = Flask(__name__)

def get_spaces(i):
    if i % 2 == 0:
        return "                    "
    return ""

def get_edges_for_app(edges: List[str]) -> Dict[str, str]:
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
            "label": f"{get_spaces(i)}{str(edge[2])}",
            "value": edge[2],
            "width": 0.5,
            "arrows": {
                "from": { "enabled": False },
                "to": { "enabled": False },
            },
        } 
        for i, edge in enumerate(edges)
    ]

@app.route("/api", methods=["GET", "POST"])
def main():
    edge1 = ("earth", "sun")
    edge2 = ("electrons", "nucleus")
    model = SentenceEmbedding()

    props_edge1 = model.get_edge_props(edge1[0], edge1[1])
    props1 = [
        {
            "id": i, 
            "x": 200,
            "y": i*40,
            "label": node, 
            "group": "0",
            "font": "12px arial #343434"
        } 
        for i, node in enumerate(props_edge1)
    ]

    props_edge2 = model.get_edge_props(edge2[0], edge2[1])
    props2 = [
        {
            "id": len(props1) + i, 
            "x": 800,
            "y": i*40,
            "label": node, 
            "group": "1",
            "font": "12px arial #343434"
        } 
        for i, node in enumerate(props_edge2)
    ]
    
    similatiry_edges = []
    for i, prop1 in enumerate(props_edge1):
        max_score = 0
        best_edge = ()
        for j, prop2 in enumerate(props_edge2):
            similatiry = model.similarity(prop1, prop2)
            if similatiry > max_score:
                max_score = similatiry
                best_edge = (i, len(props1) + j)
        if max_score > 0:
            similatiry_edges.append((best_edge[0], best_edge[1], max_score))

    return jsonify({
        "nodes": props1 + props2,
        "edges": get_edges_for_app(similatiry_edges),
    })


if __name__ == "__main__":
    app.run('localhost', port=5000, debug=True)