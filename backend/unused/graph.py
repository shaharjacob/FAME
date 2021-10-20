import sys
import time
import json
from typing import List
from pathlib import Path
from itertools import combinations

import click
from tqdm import tqdm
from click import secho
from graphviz import Digraph

backend_dir = Path(__file__).resolve().parent.parent
root = backend_dir.resolve().parent
sys.path.insert(0, str(backend_dir))
from wikifier import Wikifier
from mapping.quasimodo import Quasimodo, merge_tsvs
from mapping import concept_net, google_autosuggest

######### IMPORTANT #########
# openIE not supported here #
#############################

class MyGraph(Digraph):
    def __init__(self, name, save_database=True):
        super().__init__(name=name)
        self.init_attr()
        self.nodes = []
        self.node_names = []
        self.edges = []
        self.save_database = save_database
        self.quasimodo_edges = read_json(backend_dir / 'database' / 'quasimodo_edges.json') if save_database else {}
        self.google_edges = read_json(backend_dir / 'database' / 'google_edges.json') if save_database else {}
        self.conceptnet_edges = read_json(backend_dir / 'database' / 'conceptnet_edges.json') if save_database else {}
        self.conceptnet_nodes = read_json(backend_dir / 'database' / 'conceptnet_nodes.json') if save_database else {}
        self.quasimodo_nodes_similarity = read_json(backend_dir / 'database' / 'quasimodo_nodes_similarity.json') if save_database else {}
        self.quasimodo_nodes = read_json(backend_dir / 'database' / 'quasimodo_nodes.json') if save_database else {}
    
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

    def save_datebase(self):
        with open(backend_dir / 'database' / 'quasimodo_edges.json', 'w') as f1:
            json.dump(self.quasimodo_edges, f1, indent='\t')
        with open(backend_dir / 'database' / 'google_edges.json', 'w') as f2:
            json.dump(self.google_edges, f2, indent='\t')
        with open(backend_dir / 'database' / 'conceptnet_edges.json', 'w') as f3:
            json.dump(self.conceptnet_edges, f3, indent='\t') 
        with open(backend_dir / 'database' / 'quasimodo_nodes_similarity.json', 'w') as f4:
            json.dump(self.quasimodo_nodes_similarity, f4, indent='\t') 
        with open(backend_dir / 'database' / 'conceptnet_nodes.json', 'w') as f5:
            json.dump(self.conceptnet_nodes, f5, indent='\t')  
        with open(backend_dir / 'database' / 'quasimodo_nodes.json', 'w') as f6:
            json.dump(self.quasimodo_nodes, f6, indent='\t') 
              

def read_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def run(text: str, quasimodo: Quasimodo, addition_nouns = []):

    secho(f"Text: ", fg="blue", bold=True, nl=False)
    secho(f"{text}", fg="blue")

    # TODO
    addition_nouns = [noun for noun in addition_nouns if noun in text.split()]

    # part of speech
    w = Wikifier(text)
    nouns = w.get_specific_part_of_speech("nouns", normForm=False)
    Wikifier.remove_parts_of_compound_nouns(nouns)
    nouns = sorted(list(set(nouns + addition_nouns)))
    secho(f"Nouns: ", fg="blue", bold=True, nl=False)
    secho(f"{nouns}", fg="blue")
    graph = MyGraph(name=f'{str(backend_dir)}/graphs/{"_".join(nouns)}')

    #########
    # nodes #
    #########

    secho("\n[INFO] collect nodes information", fg="blue")
    for noun in tqdm(nouns):
        quasimodo_props, concept_net_props, concept_net_capable, concept_net_type_of, concept_net_used_for = [], [], [], [], []
        labels = {}
        
        #############
        # quasimodo #
        #############

        if noun in graph.quasimodo_nodes:
            quasimodo_props = graph.quasimodo_nodes[noun]
        else:
            quasimodo_props = quasimodo.get_entity_props(entity=noun, n_largest=10, plural_and_singular=True)
            graph.quasimodo_nodes[noun] = quasimodo_props 

        if quasimodo_props:
            labels["[Quasimodo]"] = sorted([f"{val[0]} {val[1]}" for val in quasimodo_props])


        ###############
        # concept net #
        ###############

        # has property
        if noun in graph.conceptnet_nodes and "hasProperty" in graph.conceptnet_nodes[noun]:
            concept_net_props = graph.conceptnet_nodes[noun]["hasProperty"]
        else:
            concept_net_props = concept_net.hasProperty(engine=quasimodo.engine, entity1=noun, n=10, weight_thresh=1, plural_and_singular=True)
            if noun not in graph.conceptnet_nodes:
                graph.conceptnet_nodes[noun] = {}
            graph.conceptnet_nodes[noun]["hasProperty"] = concept_net_props 
        
        if concept_net_props:
            labels["[conceptNet] has properties..."] = sorted(concept_net_props)


        # capable of
        if noun in graph.conceptnet_nodes and "capableOf" in graph.conceptnet_nodes[noun]:
            concept_net_capable = graph.conceptnet_nodes[noun]["capableOf"]
        else:
            concept_net_capable = concept_net.capableOf(engine=quasimodo.engine, entity1=noun, n=10, weight_thresh=1, plural_and_singular=True)
            if noun not in graph.conceptnet_nodes:
                graph.conceptnet_nodes[noun] = {}
            graph.conceptnet_nodes[noun]["capableOf"] = concept_net_capable 
        
        if concept_net_capable:
            labels["[conceptNet] is capable of..."] = sorted(concept_net_capable)
        

        # is a type of
        if noun in graph.conceptnet_nodes and "isA" in graph.conceptnet_nodes[noun]:
            concept_net_type_of = graph.conceptnet_nodes[noun]["isA"]
        else:
            concept_net_type_of = concept_net.isA(engine=quasimodo.engine, entity1=noun, n=10, weight_thresh=1, plural_and_singular=True)
            if noun not in graph.conceptnet_nodes:
                graph.conceptnet_nodes[noun] = {}
            graph.conceptnet_nodes[noun]["isA"] = concept_net_type_of 
        
        if concept_net_type_of:
            labels["[conceptNet] is a type of..."] = sorted(concept_net_type_of)
        

        # user for
        if noun in graph.conceptnet_nodes and "usedFor" in graph.conceptnet_nodes[noun]:
            concept_net_used_for = graph.conceptnet_nodes[noun]["usedFor"]
        else:
            concept_net_used_for = concept_net.usedFor(engine=quasimodo.engine, entity1=noun, n=10, weight_thresh=1, plural_and_singular=True)
            if noun not in graph.conceptnet_nodes:
                graph.conceptnet_nodes[noun] = {}
            graph.conceptnet_nodes[noun]["usedFor"] = concept_net_used_for 
        
        if concept_net_used_for:
            labels["[conceptNet] is used for..."] = sorted(concept_net_used_for)
            
        graph.add_node(noun, labels=labels)


    #########
    # edges #
    #########

    # extract all the combination (for directed graph)
    combs = list(combinations(nouns, 2))
    reverse_combs = [(comb[1], comb[0]) for comb in combs]
    combs += reverse_combs
    
    # create edge for every combination
    secho("\n[INFO] collect edges information from Quasimodo", fg="blue")
    for comb in tqdm(combs):
        quasimodo_props, autocomplete_props, quasimodo_nodes_props = [], [], []
        labels = {}

        # quasimodo
        if f"{comb[0]}#{comb[1]}" in graph.quasimodo_edges:
            quasimodo_props = graph.quasimodo_edges[f"{comb[0]}#{comb[1]}"]
        else:
            quasimodo_props = quasimodo.get_entities_relations(comb[0], comb[1], n_largest=10, plural_and_singular=True)
            graph.quasimodo_edges[f"{comb[0]}#{comb[1]}"] = quasimodo_props  
        
        if quasimodo_props:
            labels["from quasimido"] = sorted([f"{comb[0]} {prop} {comb[1]}" for prop in quasimodo_props])

        if f"{comb[0]}#{comb[1]}" in graph.quasimodo_nodes_similarity:
            quasimodo_nodes_props = graph.quasimodo_nodes_similarity[f"{comb[0]}#{comb[1]}"]
        else:
            quasimodo_nodes_props = quasimodo.get_similarity_between_entities(comb[0], comb[1], n_largest=10, plural_and_singular=True)
            graph.quasimodo_nodes_similarity[f"{comb[0]}#{comb[1]}"] = quasimodo_nodes_props  

        if quasimodo_nodes_props:
            labels["they are both..."] = sorted([f"{val[0]} {val[1]}" for val in quasimodo_nodes_props])

        # google auto-complete
        if f"{comb[0]}#{comb[1]}" in graph.google_edges:
            autocomplete_props = graph.google_edges[f"{comb[0]}#{comb[1]}"]
        else:
            autocomplete_props = google_autosuggest.get_entities_relations(comb[0], comb[1]).get("props", [])
            graph.google_edges[f"{comb[0]}#{comb[1]}"] = autocomplete_props  

        if autocomplete_props:
            labels["google-autocomplete"] = sorted(list(set(autocomplete_props)))
        

        # concept net
        if f"{comb[0]}#{comb[1]}" in graph.conceptnet_edges:
            concept_new_props = graph.conceptnet_edges[f"{comb[0]}#{comb[1]}"]
        else:
            concept_new_props = concept_net.get_entities_relations(comb[0], comb[1], quasimodo.engine, plural_and_singular=True)
            graph.conceptnet_edges[f"{comb[0]}#{comb[1]}"] = concept_new_props   

        if concept_new_props:
            labels["from conceptNet"] = sorted(concept_new_props)

        graph.add_edge(comb[0], comb[1], labels=labels)

    if graph.save_database:
        graph.save_datebase()
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
    tsv_to_load = root / quasimodo_path
    if not tsv_to_load.exists():
        merge_tsvs(tsv_to_load.name)  # will be created under /tsv
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
    