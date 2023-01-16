from typing import List
from pathlib import Path
from collections import Counter

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import requests
import pandas as pd
from click import secho
from bs4 import BeautifulSoup

current_dir = Path(__file__).resolve().parent


def read_page(entity1: str, entity2: str, page: int = 0, predicate: str = "") -> str:
    url = f'https://openie.allenai.org/search/?arg1={entity1}&rel={predicate}&arg2={entity2}'
    if page > 0:
        url = f'{url}&page={page}'
    try:
        response = requests.get(url)
        return response.text
    except:
        secho(f"[WARNING] Cannot read url {url}", fg="yellow", bold=True)
        return ""


# def entities_relations_wrapper(entity1: str, 
#                                entity2: str, 
#                                n: int = 10, 
#                                full_search: bool = False
#                                ) -> List[str]:
#     if full_search and n < 20:
#         secho(f"[WARNING] Page has at most 20 lines, but you asked for ({n}) with full scan.", fg="yellow", bold=True)
#     relations = []
#     get_entities_relations(relations, entity1, entity2, n=n, full_search=full_search)
    
#     # the following lines necessary for keep the order. 
#     # using list(set(relations)) will remove the order.
#     filtered_as_list = []
#     filtered_as_set = set() # for quick exists-check
#     for relation in relations:
#         if relation not in filtered_as_set:
#             filtered_as_set.add(relation)
#             filtered_as_list.append(relation)
#     return filtered_as_list


def entities_relations_wrapper(entity1: str, 
                               entity2: str, 
                               n: int = 10
                               ) -> List[str]:
    relations = []
    get_entities_relations(relations, entity1, entity2, n=n)
    return relations


def get_entity_associations_wrapper(entity: str,
                                    n: int = 10, 
                                    full_search: bool = True
                                    ) -> List[str]:

    associations = []
    get_entity_associations(associations, entity, n=n, full_search=full_search)
    
    # the following lines necessary for keep the order. 
    # using list(set(relations)) will remove the order.
    filtered_as_list = []
    filtered_as_set = set() # for quick exists-check
    for association in associations:
        if association not in filtered_as_set:
            filtered_as_set.add(association)
            filtered_as_list.append(association)
    return filtered_as_list


def get_entity_associations(associations: List[str], 
                            entity: str,
                            current_page: int = 0, 
                            n: int = 10,
                            full_search: bool = True):
    content = read_page(entity, "", current_page)
    soup = BeautifulSoup(content, 'html.parser')
    associations_parser = soup.find('div', attrs={'id': 'results-content'})
    associations_parser = associations_parser.find('div', attrs={'class': 'tabbable tabs-left'})
    associations_parser = associations_parser.find('ul', attrs={'class': 'nav nav-tabs'})
    associations_parser = associations_parser.find_all('li', attrs={'class': 'hidden-phone'})
    for association in associations_parser:
        optional_entity = association.find('span', attrs={'class': 'title-entity'})
        if optional_entity:
            association_tokens = optional_entity.text.split()
            association_tokens = [word.strip().lower() for word in association_tokens]
            associations.append(" ".join([token for token in association_tokens if token[0] != '(' and token[-1] != ')']))

        if n > 0 and len(associations) == n:
            break
    
    if full_search:
        pages = soup.find('div', attrs={'class': 'pagination'})
        if pages:
            lis = pages.find_all('li')
            for li in lis:
                if li.text.isnumeric() and int(li.text) == current_page + 1:
                    get_entity_associations(associations, entity, current_page=current_page + 1, n=n, full_search=full_search)

    

# def get_entities_relations(relations: List[str], 
#                            entity1: str, 
#                            entity2: str, 
#                            current_page: int = 0, 
#                            n: int = 10, 
#                            full_search: bool = False):
    
#     content = read_page(entity1, entity2, current_page)
#     soup = BeautifulSoup(content, 'html.parser')
#     relations_parser = soup.find('div', attrs={'id': 'results-content'})
#     relations_parser = relations_parser.find('div', attrs={'class': 'tabbable tabs-left'})
#     relations_parser = relations_parser.find('ul', attrs={'class': 'nav nav-tabs'})
#     relations_parser = relations_parser.find_all('li', attrs={'class': 'hidden-phone'})
#     for relation in relations_parser:
#         curr_relation = relation.text.split()
#         relations.append(" ".join([curr_relation[i].strip().lower() for i in range(len(curr_relation) - 1)]))
        
#         if n > 0 and  len(relations) == n:
#             break
        
#     if full_search:
#         pages = soup.find('div', attrs={'class': 'pagination'})
#         if pages:
#             lis = pages.find_all('li')
#             for li in lis:
#                 if li.text.isnumeric() and int(li.text) == current_page + 1:
#                     get_entities_relations(relations, entity1, entity2, current_page=current_page + 1, n=n, full_search=full_search)


def get_entities_relations(
    relations: List[str], 
    entity1: str, 
    entity2: str,
    n: int = 10
):
    first_letter, second_letter = entity1[0], entity1[1]
    if not (current_dir / 'openie_data' / f'{first_letter}' / f'{second_letter}.tsv').exists():
        return

    df = pd.read_csv(
        current_dir / 'openie_data' / f'{first_letter}' / f'{second_letter}.tsv', 
        sep='\t',
        names=["subject", "predicate", "object"],
        error_bad_lines=False,
        warn_bad_lines=False,
        engine='python'
    )

    df = df.loc[(df['subject'] == entity1) & (df['object'] == entity2)]
    counter = Counter(df["predicate"].tolist()).most_common(n)
    if counter:
        relations.extend([relation[0] for relation in counter])


def get_entity_suggestions_wrapper(entity: str,
                                   predicate: str, 
                                   n_largest: int = 5
                                   ) -> List[str]:

    predicate = predicate.replace('"', '')
    entities = []
    get_entity_suggestions(entities, entity, predicate, n_largest=n_largest)
    
    # the following lines necessary for keep the order. 
    # using list(set(relations)) will remove the order.
    filtered_as_list = []
    filtered_as_set = set() # for quick exists-check
    for e in entities:
        if e not in filtered_as_set:
            filtered_as_set.add(e)
            filtered_as_list.append(e)
    return filtered_as_list


def get_entity_suggestions(entities: List[str], 
                           entity: str, 
                           predicate: str, 
                           n_largest: int = 5
                           ) -> List[str]:
    content = read_page(entity1=entity, entity2="", predicate=predicate)
    soup = BeautifulSoup(content, 'html.parser')
    entities_suggestions = soup.find('div', attrs={'id': 'results-content'})
    entities_suggestions = entities_suggestions.find('div', attrs={'class': 'tabbable tabs-left'})
    entities_suggestions = entities_suggestions.find('ul', attrs={'class': 'nav nav-tabs'})
    entities_suggestions = entities_suggestions.find_all('li', attrs={'class': 'hidden-phone'})
    for entity_suggestions in entities_suggestions:
        curr_relation = entity_suggestions.text.split()
        entities.append(" ".join([curr_relation[i].strip().lower() for i in range(len(curr_relation) - 1)]))
        
        if n_largest > 0 and  len(entities) == n_largest:
            break
  

# associations = get_entity_associations_wrapper("sun")
# print(associations)

# suggestions = get_entity_suggestions_wrapper("river", "take their hands off")
# print(suggestions)