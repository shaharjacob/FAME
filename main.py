import time
from itertools import combinations

from tqdm import tqdm
from click import secho
from pathlib import Path

import concept_net
from graph import MyGraph
import google_autocomplete
from wikifier import Wikifier
from quasimodo import Quasimodo


def main(text: str, quasimodo: Quasimodo):
    graph = MyGraph()

    # part of speech
    w = Wikifier(text)
    nouns = w.get_specific_part_of_speech("nouns", normForm=False)
    Wikifier.remove_parts_of_compound_nouns(nouns)

    #########
    # nodes #
    #########

    # single noun information - for nodes
    secho("[INFO] collect nodes information", fg="blue")
    for noun in tqdm(nouns):
        labels = {}
        noun_props = quasimodo.get_subject_props(subject=noun, n_largest=10, plural_and_singular=True)
        quasimodo_props = [f"{val[0]} {val[1]}" for val in noun_props]
        if quasimodo_props:
            labels["[Quasimodo]"] = quasimodo_props
        concept_net_props = concept_net.hasProperty(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        concept_net_capable = concept_net.capableOf(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        concept_net_type_of = concept_net.isA(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        concept_net_used_for = concept_net.usedFor(engine=quasimodo.engine, subject=noun, n=10, weight_thresh=1, plural_and_singular=True)
        if concept_net_props:
            labels["[conceptNet] has properties..."] = concept_net_props
        if concept_net_capable:
            labels["[conceptNet] is caple of..."] = concept_net_capable
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
        "how do": [[comb[0], comb[1]] for comb in combs]
    }
    google_autocomplete_edges_info = google_autocomplete.process(d, verbose=False)
    
    # create edge for every combination
    secho("[INFO] collect edges information from Quasimodo", fg="blue")
    for comb in tqdm(combs):
        labels = {}
        autocomplete = google_autocomplete_edges_info.get((comb[0], comb[1]), [""])
        if autocomplete:
            labels["google-autocomplete"] = autocomplete
        
        quasimodo_subject_object_connection = quasimodo.get_subject_object_props(comb[0], comb[1], n_largest=10, plural_and_singular=True)
        if quasimodo_subject_object_connection:
            labels["from quasimido"] = [f"{comb[0]} {prop} {comb[1]}" for prop in quasimodo_subject_object_connection]

        qusimodo_subjects_similarity = quasimodo.get_similarity_between_subjects(comb[0], comb[1], n_largest=10, plural_and_singular=True)
        if qusimodo_subjects_similarity:
            labels["they are both..."] = [f"{val[0]} {val[1]}" for val in qusimodo_subjects_similarity]

        graph.add_edge(comb[0], comb[1], labels=labels)

    graph.view()  # plot the graph


if __name__ == "__main__":

    text1 = "putting a band aid on a wound is like putting a flag in the code"
    text2 = "horses in stables behave like cows in byre"
    text3 = "peanut butter has a strong taste that causes a feeling of suffocation"
    text4 = "electrons revolve around the nucleus as the earth revolve around the sun"

    tsv_to_load = Path('tsv/quasimodo.tsv')
    if not tsv_to_load.exists():
        quasimodo.merge_tsvs(tsv_to_load.name)  # will be created under /tsv
    quasimodo = Quasimodo(path=str(tsv_to_load))

    start = time.time()
    main(text4, quasimodo)
    secho(f"\nTotal running time: ", fg='blue', nl=False)
    secho(str(time.time() - start), fg='blue', bold=True)

