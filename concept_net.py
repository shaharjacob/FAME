from pathlib import Path
from typing import List, Dict, Tuple

import requests
from click import secho
from bs4 import BeautifulSoup


def read_page(subject: str, which: str, n: int = 20):
    url = f'https://conceptnet.io/c/en/{subject}?rel=/r/{which}&limit={n}'
    try:
        response = requests.get(url)
        return response.text
    except:
        secho(f"[WARNING] Cannot read url {url}", fg="yellow", bold=True)
        return ""


def extract_props(content: str, subject: str, weight_thresh: int = 0):
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
                    props.append(prop.text.strip())
    return props


def capableOf(subject: str, n: int = 20, weight_thresh: int = 0):
    content = read_page(subject, 'CapableOf', n)
    return extract_props(content, subject, weight_thresh)
    

def isA(subject: str, n: int = 20, weight_thresh: int = 0):
    content = read_page(subject, 'IsA', n)
    return extract_props(content, subject, weight_thresh)


def usedFor(subject: str, n: int = 20, weight_thresh: int = 0):
    content = read_page(subject, 'UsedFor', n)
    return extract_props(content, subject, weight_thresh)


def hasProperty(subject: str, n: int = 20, weight_thresh: int = 0):
    content = read_page(subject, 'HasProperty', n)
    return extract_props(content, subject, weight_thresh)


# print(capableOf('sun', 10, 1))
# print(isA('sun', 10, 1))
# print(usedFor('sun', 10, 1))
# print(hasProperty('sun', 10, 1))