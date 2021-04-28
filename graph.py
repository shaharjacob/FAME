from typing import List

from click import secho
from graphviz import Digraph

class MyGraph(Digraph):
    def __init__(self):
        super().__init__()
        self.init_attr()
        self.nodes = []
        self.node_names = []
        self.edges = []
    
    def init_attr(self):
        self.attr('graph', pad='1', ranksep='1', nodesep='1')
        self.attr('node', shape='note')
    
    def add_node(self, name: str, labels: List[str] = [""], font_color: str = 'black', font_size: int = 8):
        if name in self.node_names:
            secho(f"[WARNING] '{name}' already added.", fg="yellow", bold=True)
            return
        self.node_names.append(name)
        self.nodes.append({
            "name": name,
            "labels": labels,
            "font_color": font_color,
            "font_size": font_size,
        })
        props_in_html = MyGraph.get_labels_as_html(labels, font_color, font_size, name)
        self.node(name, props_in_html)

    def add_edge(self, head: str, tail: str, labels: List[str] = [""], font_color: str = 'black', font_size: int = 8):
        if (head not in self.node_names) or (tail not in self.node_names):
            secho(f"[ERROR] '{head}' or '{tail}' not exists in nodes list.", fg="red", bold=True)
            secho(f"        list nodes is: {self.node_names}", fg="red")
            exit(1)
        self.edges.append({
            "head": head,
            "tail": tail,
            "labels": labels if labels else [""],
            "font_color": font_color,
            "font_size": font_size,
        })
        props_in_html = MyGraph.get_labels_as_html(labels if labels else [""], font_color, font_size, "")
        self.edge(head, tail, props_in_html)

    @staticmethod
    def get_labels_as_html(labels: List[str], font_color: str, font_size: str, name: str) -> str:
        parts = ['<']
        parts.append(f'<font color="{font_color}" point-size="{font_size}px">')
        parts.append('<table border="0" cellspacing="0" cellpadding="0">')
        if name: # node
            parts.append(f'<tr><td><u><b>{name}</b></u></td></tr>')
        if isinstance(labels, dict):  # edge
            for title, labels_ in labels.items():
                parts.append(f'<tr><td><u><b>{title}</b></u></td></tr>')
                for label in labels_:
                    parts.append(f'<tr><td>{label}</td></tr>')
                parts.append(f'<tr><td> </td></tr>')
        else: # node
            for label in labels:
                parts.append(f'<tr><td>{label}</td></tr>')
        parts.append('</table></font>>')
        return ''.join(parts)
    
    def view(self):
        super().view()        



# graph = MyGraph()
# graph.add_node("horse", labels=['first', 'second', 'third', 'first', 'second', 'third'], font_color='blue')
# graph.add_node("cow")
# graph.add_node("chicken")
# graph.add_edge('horse', 'cow', labels=['first', 'second', 'third'], font_color='green')
# graph.add_edge('cow', 'horse', labels=['first', 'second', 'third'])
# graph.add_edge('horse', 'chicken', labels=['first', 'second', 'third'])
# graph.add_edge('chicken', 'horse', labels=['first', 'second', 'third'])
# graph.add_edge('cow', 'chicken', labels=['first', 'second', 'third'])
# graph.add_edge('chicken', 'cow', labels=['first', 'second', 'third'])
# graph.view()
