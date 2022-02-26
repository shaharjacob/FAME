import json
from pathlib import Path
from typing import List, Set, NoReturn, Tuple

import inflect
import requests
from click import secho
from bs4 import BeautifulSoup

root = Path(__file__).resolve().parent.parent.parent

def read_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def read_page(entity: str, which: str, n: int = 20) -> str:
    url = f'https://conceptnet.io/c/en/{entity}?rel=/r/{which}&limit={n}'
    try:
        response = requests.get(url)
        return response.text
    except:
        secho(f"[WARNING] Cannot read url {url}", fg="yellow", bold=True)
        return ""


def extend_plural_and_singular(engine: inflect.engine, entity: str, list_to_update: List[str]) -> NoReturn:
    # we wil check for plural and singular of the entity
    plural = engine.plural(entity)
    if plural and plural not in list_to_update:
        list_to_update.append(plural)

    singular = engine.singular_noun(entity)
    if singular and singular not in list_to_update:
        list_to_update.append(singular)


def extract_props(content: str, entity: str, matches: Set[str], weight_thresh: int = 0) -> List[Tuple[str, float]]:
    soup = BeautifulSoup(content, 'html.parser')
    # TODO: add test for that API
    tds = soup.find_all('td', attrs={'class': 'edge-end'})
    weights = soup.find_all('div', attrs={'class': 'weight'})
    entities = soup.find_all('td', attrs={'class': 'edge-start'})
    props = []
    for td, weight, td_entity in zip(tds, weights, entities):
        prop = td.find('a')
        if prop:
            w = float(weight.text.strip().split(':')[1].strip())
            if w >= weight_thresh: # we want only props that bigger then the threshold
                actual_entity = td_entity.find('a').text.strip()
                if entity in actual_entity:
                    # we check if our real entity include in the actual. This prevent noise
                    prop_to_add = prop.text.strip()
                    if (prop_to_add not in matches) and (prop_to_add != entity):
                        matches.add(prop_to_add)  # this set use for quick check if exists
                        props.append((prop_to_add, w))
    return props


def extend_and_extract_props(engine: inflect.engine, which: str, entity1: str, n: int = 20, weight_thresh: int = 0, plural_and_singular: bool = False, entity2: str = "") -> List[str]:
    # which: CapableOf, IsA, UsedFor, HasProperty
    entities = [entity1]
    if plural_and_singular:
        extend_plural_and_singular(engine, entity1, entities)

    all_props = []
    matches = set()
    for entity in entities:
        content = read_page(entity, which, n)
        props = extract_props(content, entity, matches, weight_thresh)
        all_props.extend(props)
    
    # sorting by the weight that extracted with the prop
    all_props = sorted(all_props, key=lambda x: -x[1])
    all_props = [val[0] for val in all_props[:n] if val[0] and val[0] != entity1 and val[0] != entity2]

    # we will take only props that end with the entity2. 
    # we will find pattern like <entity1> .* <entity2>
    if entity2:
        new_props = []
        for prop in all_props:
            if prop.endswith(entity2):
                new_props.append(prop[:-len(entity2)].strip())
        all_props = new_props
    return sorted(all_props)


def capableOf(engine: inflect.engine, entity1: str, n: int = 20, weight_thresh: int = 0, plural_and_singular: bool = False, entity2: str = "") -> List[str]:
    return extend_and_extract_props(engine, "CapableOf", entity1, n, weight_thresh, plural_and_singular, entity2)
    

def isA(engine: inflect.engine, entity1: str, n: int = 20, weight_thresh: int = 0, plural_and_singular: bool = False, entity2: str = "") -> List[str]:
    return extend_and_extract_props(engine, "IsA", entity1, n, weight_thresh, plural_and_singular, entity2)


def usedFor(engine: inflect.engine, entity1: str, n: int = 20, weight_thresh: int = 0, plural_and_singular: bool = False, entity2: str = "") -> List[str]:
    return extend_and_extract_props(engine, "UsedFor", entity1, n, weight_thresh, plural_and_singular, entity2)


def hasProperty(engine: inflect.engine, entity1: str, n: int = 20, weight_thresh: int = 0, plural_and_singular: bool = False, entity2: str = "") -> List[str]:
    return extend_and_extract_props(engine, "HasProperty", entity1, n, weight_thresh, plural_and_singular, entity2)


def get_entities_relations(entity1: str, entity2: str, engine: inflect.engine = None, n_best: int = 100, weight_thresh: int = 1, plural_and_singular: bool = False) -> List[str]:
    if not engine:
        engine = inflect.engine()

    # find patterns like: entity1 .* entity2
    has_props = hasProperty(engine, entity1, n_best, weight_thresh, plural_and_singular, entity2)
    capable_of = capableOf(engine, entity1, n_best, weight_thresh, plural_and_singular, entity2)
    type_of = isA(engine, entity1, n_best, weight_thresh, plural_and_singular, entity2)
    used_for = usedFor(engine, entity1, n_best, weight_thresh, plural_and_singular, entity2)
    return has_props + capable_of + type_of + used_for


# def get_entity_props(entity: str, engine: inflect.engine = None, n_best: int = 5, weight_thresh: int = 1, plural_and_singular: bool = False, override_db: bool = False) -> List[str]:
#     if not engine and plural_and_singular:
#         engine = inflect.engine()

#     # we want the props of a single entity
#     # we first check if the entity exists in the db - if not, we extract if from the conceptNet API.
#     conceptnet_db = read_json(root / 'backend' / 'database' / 'conceptnet_nodes.json')
#     should_save = False

#     if entity not in conceptnet_db:
#         conceptnet_db[entity] = {}
#         should_save = True

#     if "hasProperty" not in conceptnet_db[entity] or override_db:
#         conceptnet_db[entity]["hasProperty"] = hasProperty(engine, entity, n_best, weight_thresh, plural_and_singular)
#         should_save = True
    
#     if "capableOf" not in conceptnet_db[entity] or override_db:
#         conceptnet_db[entity]["capableOf"] = capableOf(engine, entity, n_best, weight_thresh, plural_and_singular)
#         should_save = True

#     if "isA" not in conceptnet_db[entity] or override_db:
#         conceptnet_db[entity]["isA"] = isA(engine, entity, n_best, weight_thresh, plural_and_singular)
#         should_save = True

#     if "usedFor" not in conceptnet_db[entity] or override_db:
#         conceptnet_db[entity]["usedFor"] = usedFor(engine, entity, n_best, weight_thresh, plural_and_singular)
#         should_save = True
    
#     if should_save:
#         with open(root / 'backend' / 'database' / 'conceptnet_nodes.json', 'w') as f:
#             json.dump(conceptnet_db, f, indent='\t')
            
#     # sorting for abc..
#     return sorted(list(set(conceptnet_db[entity]["hasProperty"] + conceptnet_db[entity]["capableOf"] + conceptnet_db[entity]["isA"] + conceptnet_db[entity]["usedFor"])))


if __name__ == '__main__':
    # res = get_entity_props("earth", n_best=10)
    # print(res)
    pass