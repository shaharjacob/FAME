import time
from typing import List
from pathlib import Path
from itertools import combinations

import click
from tqdm import tqdm
from click import secho
from graphviz import Digraph

import concept_net
import google_autocomplete
from wikifier import Wikifier
from quasimodo import Quasimodo


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


def run(text: str, quasimodo: Quasimodo, addition_nouns = []):

    secho(f"Text: ", fg="blue", bold=True, nl=False)
    secho(f"{text}", fg="blue")

    # part of speech
    w = Wikifier(text)
    nouns = w.get_specific_part_of_speech("nouns", normForm=False)
    Wikifier.remove_parts_of_compound_nouns(nouns)
    nouns = sorted(list(set(nouns + addition_nouns)))
    secho(f"Nouns: ", fg="blue", bold=True, nl=False)
    secho(f"{nouns}", fg="blue")
    graph = MyGraph(name=f'graphs/{"_".join(nouns)}')

    #########
    # nodes #
    #########

    secho("\n[INFO] collect nodes information", fg="blue")
    for noun in tqdm(nouns):
        labels = {}
        noun_props = quasimodo.get_node_props(node=noun, n_largest=10, plural_and_singular=True)
        quasimodo_props = [f"{val[0]} {val[1]}" for val in noun_props]
        concept_net_props = concept_net.hasProperty(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        concept_net_capable = concept_net.capableOf(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        concept_net_type_of = concept_net.isA(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        concept_net_used_for = concept_net.usedFor(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        
        if quasimodo_props:
            labels["[Quasimodo]"] = quasimodo_props
        if concept_net_props:
            labels["[conceptNet] has properties..."] = concept_net_props
        if concept_net_capable:
            labels["[conceptNet] is capable of..."] = concept_net_capable
        if concept_net_type_of:
            labels["[conceptNet] is a type of..."] = concept_net_type_of
        if concept_net_used_for:
            labels["[conceptNet] is used for..."] = concept_net_used_for
            
        graph.add_node(noun, labels=labels)


    #########
    # edges #
    #########

    # extract all the combination (for directed graph)
    combs = list(combinations(nouns, 2))
    reverse_combs = [(comb[1], comb[0]) for comb in combs]
    combs += reverse_combs

    # google autocomlete - for edges
    d = {
        "why do": [[comb[0], comb[1]] for comb in combs],
        "why does": [[comb[0], comb[1]] for comb in combs],
        "how do": [[comb[0], comb[1]] for comb in combs],
        "how does": [[comb[0], comb[1]] for comb in combs],
    }
    google_autocomplete_edges_info = google_autocomplete.process(d, verbose=False)
    
    # create edge for every combination
    secho("\n[INFO] collect edges information from Quasimodo", fg="blue")
    for comb in tqdm(combs):
        labels = {}
        autocomplete = google_autocomplete_edges_info.get((comb[0], comb[1]), {"suggestions": [], "props": []}).get("props", [])
        if autocomplete:
            labels["google-autocomplete"] = autocomplete
        
        quasimodo_subject_object_connection = quasimodo.get_edge_props(comb[0], comb[1], n_largest=10, plural_and_singular=True)
        if quasimodo_subject_object_connection:
            labels["from quasimido"] = [f"{comb[0]} {prop} {comb[1]}" for prop in quasimodo_subject_object_connection]

        qusimodo_subjects_similarity = quasimodo.get_similarity_between_nodes(comb[0], comb[1], n_largest=10, plural_and_singular=True)
        if qusimodo_subjects_similarity:
            labels["they are both..."] = [f"{val[0]} {val[1]}" for val in qusimodo_subjects_similarity]
        
        concept_net_props = concept_net.hasProperty(engine=quasimodo.engine, subject=comb[0], n=1000, weight_thresh=1, plural_and_singular=True, obj=comb[1])
        concept_net_capable = concept_net.capableOf(engine=quasimodo.engine, subject=comb[0], n=1000, weight_thresh=1, plural_and_singular=True, obj=comb[1])
        concept_net_type_of = concept_net.isA(engine=quasimodo.engine, subject=comb[0], n=100, weight_thresh=1, plural_and_singular=True, obj=comb[1])
        concept_net_used_for = concept_net.usedFor(engine=quasimodo.engine, subject=comb[0], n=1000, weight_thresh=1, plural_and_singular=True, obj=comb[1])
        all_concept_net_props = concept_net_props + concept_net_capable + concept_net_type_of + concept_net_used_for
        if all_concept_net_props:
            labels["from conceptNet"] = all_concept_net_props

        graph.add_edge(comb[0], comb[1], labels=labels)

    graph.view()  # plot the graph


@click.command()
@click.option('-t', '--text', default="electrons revolve around the nucleus as the earth revolve around the sun", 
                help="The text you want to visualize")
@click.option('-a', '--addition-nouns', default=[], multiple=True, 
                help="Addition nouns in case of Wikifier is failed to recognize (sunscreen)")
@click.option('-q', '--quasimodo-path', default="tsv/quasimodo.tsv", 
                help="Path to load quasimodo (the tsv file")
def main(text, addition_nouns, quasimodo_path):
    start = time.time()
    tsv_to_load = Path(quasimodo_path)
    if not tsv_to_load.exists():
        import quasimodo as qs
        qs.merge_tsvs(tsv_to_load.name)  # will be created under /tsv
    quasimodo = Quasimodo(path=str(tsv_to_load))
    run(text, quasimodo, addition_nouns=list(addition_nouns))
    secho(f"\nTotal running time: ", fg='blue', nl=False)
    secho(str(time.time() - start), fg='blue', bold=True)

if __name__ == "__main__":
    main()
    # text1 = "putting a band aid on a wound is like putting a flag in the code"
    # text2 = "horses in stables behave like cows in byre"
    # text3 = "electrons revolve around the nucleus as the earth revolve around the sun"

    # text4 = "peanut butter has a strong taste that causes a feeling of suffocation"
    # text5 = "The nucleus, which is positively charged, and the electrons which are negatively charged, compose the atom"
    # text6 = "On earth, the atmosphere protects us from the sun, but not enough so we use sunscreen"

    