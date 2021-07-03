import time
from itertools import combinations

from tqdm import tqdm
from click import secho
from pathlib import Path

import concept_net
import quasimodo as qs
import google_autosuggest
from quasimodo import Quasimodo


def intersection(lst1, lst2):
    return [value for value in lst1 if value in lst2]


def main(relation: str, quasimodo: Quasimodo):

    paris = relation.split('~')
    pair1 = paris[0].strip().split(':')
    pair2 = paris[1].strip().split(':')
    pair11 = pair1[0].strip()
    pair12 = pair1[1].strip()
    pair21 = pair2[0].strip()
    pair22 = pair2[1].strip()

    # pair11 & pair12 common properties
    qusimodo_subjects_similarity = quasimodo.get_similarity_between_nodes(pair11, pair12, n_largest=10, plural_and_singular=True)
    quasimodo_common_props = [f"{val[0]} {val[1]}" for val in qusimodo_subjects_similarity]

    pair11_props = concept_net.hasProperty(engine=quasimodo.engine, subject=pair11, n=10, weight_thresh=1, plural_and_singular=True)
    pair12_props = concept_net.hasProperty(engine=quasimodo.engine, subject=pair12, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_props = intersection(pair11_props, pair12_props)

    pair11_props = concept_net.capableOf(engine=quasimodo.engine, subject=pair11, n=10, weight_thresh=1, plural_and_singular=True)
    pair12_props = concept_net.capableOf(engine=quasimodo.engine, subject=pair12, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_capable = intersection(pair11_props, pair12_props)

    pair11_props = concept_net.isA(engine=quasimodo.engine, subject=pair11, n=10, weight_thresh=1, plural_and_singular=True)
    pair12_props = concept_net.isA(engine=quasimodo.engine, subject=pair12, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_type_of = intersection(pair11_props, pair12_props)

    pair11_props = concept_net.usedFor(engine=quasimodo.engine, subject=pair11, n=10, weight_thresh=1, plural_and_singular=True)
    pair12_props = concept_net.usedFor(engine=quasimodo.engine, subject=pair12, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_used_for = intersection(pair11_props, pair12_props)

    if quasimodo_common_props or concept_net_common_props or concept_net_common_capable or concept_net_common_type_of or concept_net_common_used_for:
        secho(f"{pair11} ~ {pair12} common props", fg="blue", bold=True)

    if quasimodo_common_props:
        secho(f"  - Properties for quasimodo:", fg="blue")
        for prop in quasimodo_common_props:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_props:
        secho(f"  - Properties for conceptNet:", fg="blue")
        for prop in concept_net_common_props:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_capable:
        secho(f"  - They are both capable of:", fg="blue")
        for prop in concept_net_common_capable:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_type_of:
        secho(f"  - They are both type of:", fg="blue")
        for prop in concept_net_common_type_of:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_used_for:
        secho(f"  - They are both used for:", fg="blue")
        for prop in concept_net_common_used_for:
            secho(f"    - {prop}", fg="blue")


    print()
    # pair21 & pair22 common properties
    qusimodo_subjects_similarity = quasimodo.get_similarity_between_nodes(pair21, pair22, n_largest=10, plural_and_singular=True)
    quasimodo_common_props = [f"{val[0]} {val[1]}" for val in qusimodo_subjects_similarity]

    pair21_props = concept_net.hasProperty(engine=quasimodo.engine, subject=pair21, n=10, weight_thresh=1, plural_and_singular=True)
    pair22_props = concept_net.hasProperty(engine=quasimodo.engine, subject=pair22, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_props = intersection(pair21_props, pair22_props)

    pair21_props = concept_net.capableOf(engine=quasimodo.engine, subject=pair21, n=10, weight_thresh=1, plural_and_singular=True)
    pair22_props = concept_net.capableOf(engine=quasimodo.engine, subject=pair22, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_capable = intersection(pair21_props, pair22_props)

    pair21_props = concept_net.isA(engine=quasimodo.engine, subject=pair21, n=10, weight_thresh=1, plural_and_singular=True)
    pair22_props = concept_net.isA(engine=quasimodo.engine, subject=pair22, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_type_of = intersection(pair21_props, pair22_props)

    pair21_props = concept_net.usedFor(engine=quasimodo.engine, subject=pair21, n=10, weight_thresh=1, plural_and_singular=True)
    pair22_props = concept_net.usedFor(engine=quasimodo.engine, subject=pair22, n=10, weight_thresh=1, plural_and_singular=True)
    concept_net_common_used_for = intersection(pair21_props, pair22_props)

    if quasimodo_common_props or concept_net_common_props or concept_net_common_capable or concept_net_common_type_of or concept_net_common_used_for:
        secho(f"{pair21} ~ {pair22} common props", fg="blue", bold=True)

    if quasimodo_common_props:
        secho(f"  - Properties for quasimodo:", fg="blue")
        for prop in quasimodo_common_props:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_props:
        secho(f"  - Properties for conceptNet:", fg="blue")
        for prop in concept_net_common_props:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_capable:
        secho(f"  - They are both capable of:", fg="blue")
        for prop in concept_net_common_capable:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_type_of:
        secho(f"  - They are both type of:", fg="blue")
        for prop in concept_net_common_type_of:
            secho(f"    - {prop}", fg="blue")

    if concept_net_common_used_for:
        secho(f"  - They are both used for:", fg="blue")
        for prop in concept_net_common_used_for:
            secho(f"    - {prop}", fg="blue")


    print()
    # sun --> earth, nucleus --> electrons
    connection_11_21 = quasimodo.get_edge_props(pair11, pair21, n_largest=10, plural_and_singular=True)
    connection_12_22 = quasimodo.get_edge_props(pair12, pair22, n_largest=10, plural_and_singular=True)
    connections = intersection(connection_11_21, connection_12_22)
    if connections:
        secho(f"{pair11} --> {pair21}, {pair12} --> {pair22}", fg="blue", bold=True)
        for prop in connections:
            secho(f"  - {prop}", fg="blue")
    

    print()
    # earth --> sun, electrons --> nucleus
    connection_21_11 = quasimodo.get_edge_props(pair21, pair11, n_largest=10, plural_and_singular=True)
    connection_22_12 = quasimodo.get_edge_props(pair22, pair12, n_largest=10, plural_and_singular=True)
    connections = intersection(connection_21_11, connection_22_12)
    if connections:
        secho(f"{pair21} --> {pair11}, {pair22} --> {pair12}", fg="blue", bold=True)
        for prop in connections:
            secho(f"  - {prop}", fg="blue")


if __name__ == "__main__":

    text = "sun:nucleus ~ earth:electrons"

    tsv_to_load = Path('tsv/quasimodo.tsv')
    if not tsv_to_load.exists():
        qs.merge_tsvs(tsv_to_load.name)  # will be created under /tsv
    quasimodo = Quasimodo(path=str(tsv_to_load))

    start = time.time()
    main(text, quasimodo)
    secho(f"\nTotal running time: ", fg='blue', nl=False)
    secho(str(time.time() - start), fg='blue', bold=True)

