from typing import List

import requests
from click import secho
from bs4 import BeautifulSoup


def read_page(entity1: str, entity2: str, page: int = 0) -> str:
    url = f'https://openie.allenai.org/search/?arg1={entity1}&arg2={entity2}'
    if page > 0:
        url = f'{url}&page={page}'
    try:
        response = requests.get(url)
        return response.text
    except:
        secho(f"[WARNING] Cannot read url {url}", fg="yellow", bold=True)
        return ""


def entities_relations_wrapper(entity1: str, entity2: str, n: int = 10) -> List[str]:
    relations = []
    get_entities_relations(relations, entity1, entity2, n=n)
    return list(set(relations))


def get_entities_relations(relations: List[str], entity1: str, entity2: str, current_page: int = 0, n: int = 10):
    content = read_page(entity1, entity2)
    soup = BeautifulSoup(content, 'html.parser')
    relations_parser = soup.find('div', attrs={'id': 'results-content'})
    relations_parser = relations_parser.find('div', attrs={'class': 'tabbable tabs-left'})
    relations_parser = relations_parser.find('ul', attrs={'class': 'nav nav-tabs'})
    relations_parser = relations_parser.find_all('li', attrs={'class': 'hidden-phone'})
    for relation in relations_parser:
        curr_relation = relation.text.split()
        relations.append(" ".join([curr_relation[i].strip().lower() for i in range(len(curr_relation) - 1)]))
        if n > 0 and  len(relations) == n:
            break
    # pages = soup.find('div', attrs={'class': 'pagination'})
    # if pages:
    #     lis = pages.find_all('li')
    #     for li in lis:
    #         if li.text.isnumeric() and int(li.text) == current_page + 1:
    #             get_entities_relations(relations, entity1, entity2, current_page + 1)
