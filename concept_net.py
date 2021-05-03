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
                    if prop.text.strip() not in matches:
                        matches.add(prop.text.strip())
                        props.append((prop.text.strip(), w))
    return props


def extend_and_extract_props(engine: inflect.engine, 
                             which: str, 
                             subject: str, 
                             n: int = 20, 
                             weight_thresh: int = 0,
                             plural_and_singular: bool = False):
    subjects = [subject]
    if plural_and_singular:
        extend_plural_and_singular(engine, subject, subjects)

    to_return = []
    matches = set()
    for sub in subjects:
        content = read_page(subject, which, n)
        props = extract_props(content, subject, matches, weight_thresh)
        to_return.extend(props)
    to_return = sorted(to_return, key=lambda x: -x[1])
    return [val[0] for val in to_return[:n]]


def capableOf(engine: inflect.engine, 
              subject: str, 
              n: int = 20, 
              weight_thresh: int = 0,
              plural_and_singular: bool = False):
    return extend_and_extract_props(engine, "CapableOf", subject, n, weight_thresh, plural_and_singular)
    

def isA(engine: inflect.engine, 
        subject: str, 
        n: int = 20, 
        weight_thresh: int = 0,
        plural_and_singular: bool = False):
    return extend_and_extract_props(engine, "IsA", subject, n, weight_thresh, plural_and_singular)


def usedFor(engine: inflect.engine, 
            subject: str, 
            n: int = 20, 
            weight_thresh: int = 0,
            plural_and_singular: bool = False):
    return extend_and_extract_props(engine, "UsedFor", subject, n, weight_thresh, plural_and_singular)


def hasProperty(engine: inflect.engine, 
                subject: str, 
                n: int = 20, 
                weight_thresh: int = 0,
                plural_and_singular: bool = False):
    return extend_and_extract_props(engine, "HasProperty", subject, n, weight_thresh, plural_and_singular)


# print(capableOf('sun', 10, 1))
# print(isA('sun', 10, 1))
# print(usedFor('sun', 10, 1))
# print(hasProperty('sun', 10, 1))