from pathlib import Path
from typing import List, Dict, Tuple, Set

import inflect
import requests
from click import secho
from bs4 import BeautifulSoup


def read_page(subject: str, 
              which: str, 
              n: int = 20):
    url = f'https://conceptnet.io/c/en/{subject}?rel=/r/{which}&limit={n}'
    try:
        response = requests.get(url)
        return response.text
    except:
        secho(f"[WARNING] Cannot read url {url}", fg="yellow", bold=True)
        return ""


def extend_plural_and_singular(engine: inflect.engine,
                               string: str,
                               list_to_update: List[str]):

    plural = engine.plural(string)
    if plural and plural not in list_to_update:
        list_to_update.append(plural)

    singular = engine.singular_noun(string)
    if singular and singular not in list_to_update:
        list_to_update.append(singular)


def extract_props(content: str, 
                  subject: str, 
                  matches: Set[str],
                  weight_thresh: int = 0):
    soup = BeautifulSoup(content, 'html.parser')
    tds = soup.find_all('td', attrs={'class': 'edge-end'})
    weights = soup.find_all('div', attrs={'class': 'weight'})
    subjects = soup.find_all('td', attrs={'class': 'edge-start'})
    props = []
    for td, weight, td_subject in zip(tds, weights, subjects):
        prop = td.find('a')
        if prop:
            w = float(weight.text.strip().split(':')[1].strip())
            if w >= weight_thresh:
                subject_ = td_subject.find('a').text.strip()
                if subject in subject_:
                    prop_to_add = prop.text.strip()
                    if (prop_to_add not in matches) and (prop_to_add != subject):
                        matches.add(prop_to_add)
                        props.append((prop_to_add, w))
    return props


def extend_and_extract_props(engine: inflect.engine, 
                             which: str, 
                             subject: str, 
                             n: int = 20, 
                             weight_thresh: int = 0,
                             plural_and_singular: bool = False,
                             obj: str = ""):
    subjects = [subject]
    if plural_and_singular:
        extend_plural_and_singular(engine, subject, subjects)

    all_props = []
    matches = set()
    for sub in subjects:
        content = read_page(sub, which, n)
        props = extract_props(content, sub, matches, weight_thresh)
        all_props.extend(props)
    all_props = sorted(all_props, key=lambda x: -x[1])
    all_props = [val[0] for val in all_props[:n]]

    if obj:
        new_props = []
        for prop in all_props:
            if prop.endswith(obj):
                new_props.append(prop[:-len(obj)].strip())
        all_props = new_props
    return all_props


def capableOf(engine: inflect.engine, 
              subject: str, 
              n: int = 20, 
              weight_thresh: int = 0,
              plural_and_singular: bool = False,
              obj: str = ""):
    return extend_and_extract_props(engine, "CapableOf", subject, n, weight_thresh, plural_and_singular, obj)
    

def isA(engine: inflect.engine, 
        subject: str, 
        n: int = 20, 
        weight_thresh: int = 0,
        plural_and_singular: bool = False,
        obj: str = ""):
    return extend_and_extract_props(engine, "IsA", subject, n, weight_thresh, plural_and_singular, obj)


def usedFor(engine: inflect.engine, 
            subject: str, 
            n: int = 20, 
            weight_thresh: int = 0,
            plural_and_singular: bool = False,
            obj: str = ""):
    return extend_and_extract_props(engine, "UsedFor", subject, n, weight_thresh, plural_and_singular, obj)


def hasProperty(engine: inflect.engine, 
                subject: str, 
                n: int = 20, 
                weight_thresh: int = 0,
                plural_and_singular: bool = False,
                obj: str = ""):
    return extend_and_extract_props(engine, "HasProperty", subject, n, weight_thresh, plural_and_singular, obj)



engine = inflect.engine()
props = usedFor(engine=engine, subject='umbrella', n=1000, weight_thresh=1, plural_and_singular=True, obj='rain')
print(props)
