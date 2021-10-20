from typing import List

import requests
from click import secho
from bs4 import BeautifulSoup

def read_page(entity: str, page: int) -> str:
    url = f'https://wordassociations.net/en/words-associated-with/{entity}?start={(page- 1) * 100}'
    try:
        response = requests.get(url)
        return response.text
    except:
        secho(f"[WARNING] Cannot read url {url}", fg="yellow", bold=True)
        return ""

def get_associations(entity: str) -> List[str]:
    words = []
    page = 1
    while True:
        content = read_page(entity, page)
        soup = BeautifulSoup(content, 'html.parser')
        div = soup.find('div', attrs={'class': 'section NOUN-SECTION'})
        if not div:
            break
        entries = [entry.text.lower() for entry in div.find_all('li')]
        words += entries
        page += 1
    return words


def get_intersection(entity1: str, entity2: str, n: int = 0) -> List[str]:
    words1 = get_associations(entity1)
    words2 = get_associations(entity2)
    intersection = sorted([(value, i + words2.index(value)) for i, value in enumerate(words1) if value in words2], key=lambda x: x[1])
    if n > 0:
        intersection = intersection[:n]
    return [val[0] for val in intersection]

# res = get_intersection('sun', 'planet')
res = get_intersection('nucleus', 'electrons')
print(res)













# url = 'https://api.wordassociations.net/associations/v1.0/json/search?text=%s&lang=%s&limit=%s&pos=%s'
# response = requests.get(url % ('sun', 'en', 300, 'noun')).text
# print(response)



