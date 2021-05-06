import glob
from typing import List

from click import secho
from graphviz import Digraph
# f"graphs/{len(glob.glob('graphs/*.pdf'))}"

class MyGraph(Digraph):
    def __init__(self, name):
        super().__init__(name=name)
        self.init_attr()
        self.nodes = []
        self.node_names = []
        self.edges = []
    
    def init_attr(self):
        self.attr('graph', pad='1', ranksep='1', nodesep='1')
        self.attr('node', shape='note')
    
    def add_node(self, name: str, labels: List[str] = [""], font_color: str = 'black', font_size: int = 10):
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

    def add_edge(self, head: str, tail: str, labels: List[str] = [""], font_color: str = 'black', font_size: int = 10):
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
        parts.append(f'<FONT FACE="Segoe UI">')
        parts.append('<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="0">')
        if name: # node
            parts.append(f'<TR><TD><FONT POINT-SIZE="{font_size + 6}"><U><B>{name}</B></U></FONT></TD></TR>')
        if isinstance(labels, dict):  # edge
            for title, labels_ in labels.items():
                parts.append(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="{font_size}" COLOR="#494949"><B>{title}</B></FONT></TD></TR>')
                for label in labels_:
                    parts.append(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="{font_size}" COLOR="#333333">- {label}</FONT></TD></TR>')
                parts.append(f'<TR><TD> </TD></TR>')
        else: # node
            for label in labels:
                parts.append(f'<TR><TD>{label}</TD></TR>')
        parts.append('</TABLE></FONT>>')
        return ''.join(parts)
    
    def view(self):
        super().view()        

