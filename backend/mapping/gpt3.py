import re
import os
import json
import time
import inflect
from pathlib import Path

import yaml
import openai
from openai.error import AuthenticationError
from tqdm import tqdm

BACKEND_DIR = Path(__file__).resolve().parent.parent
EVALUATION_FOLDER = BACKEND_DIR / 'evaluation'
DATABASE_FOLDER = BACKEND_DIR / 'database'

OPENAI_API_KEY= os.environ.get("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY

prompt = [
    "Q: What is the relations between blizzard and snowflake?",
    "A: A blizzard produces snowflakes.",
    "A: A blizzard contains a lot of snowflakes.",
    "",
    "Q: What is the relations between umbrella and rain?",
    "A: An umbrella protects from rain.",
    "A: An umbrella prevent rain.",
    "",
    "Q: What is the relations between movie and screen?",
    "A: Movie displayed on the screen",
    "A: Movie can be shown on the screen",
    "A: Movie use green screen",
    "",
    "Q: What is the relations between gravity and newton?",
    "A: newton discovered gravity",
    "A: newton related to gravity",
    "",
    "Q: What is the relations between electron and nucleus?",
    "A: An electron revolves around nucleus.",
    "A: An electron is mush smaller then nucleus.",
    "A: An electron attracts nucleus.",
    "",
]

def get_entities_relations(entity1: str, entity2: str, engine: inflect.engine):
    with open(DATABASE_FOLDER / 'gpt3_edges.json', 'r') as f:
        content = json.load(f)

    should_save = False
    if f"{entity1}#{entity2}" not in content:
        content[f"{entity1}#{entity2}"] = get_entities_relations_api(entity1, entity2)
        should_save = True
        time.sleep(1)

    # if f"{entity2}#{entity1}" not in content:
    #     content[f"{entity2}#{entity1}"] = get_entities_relations_api(entity2, entity1)
    #     should_save = True
    #     time.sleep(1)
    
    if should_save:
        with open(DATABASE_FOLDER / 'gpt3_edges.json', 'w') as fw:
            json.dump(content, fw, indent='\t')

    relation_as_set = set()
    # relations = list(set(content[f"{entity1}#{entity2}"] + content[f"{entity2}#{entity1}"]))
    relations = list(set(content[f"{entity1}#{entity2}"]))
    for relation in relations:
        relation = relation.lower()
        match = re.search(f'{entity1} (.*?) {entity2}', relation)
        if match:
            relation = match.group(1).strip()
            if relation:
                relation_as_set.add(relation)
        else:
            if not engine:
                engine = inflect.engine()
            entity2 = engine.plural(entity2)
            match = re.search(f'{entity1} (.*?) {entity2}', relation)
            if match:
                relation = match.group(1).strip()
                if relation:
                    relation_as_set.add(relation)
    
    return list(relation_as_set)



def get_entities_relations_api(entity1: str, entity2: str):
    question = [f"Q: What is the relations between {entity1} and {entity2}?"]
    prompt_s =  "\n".join(prompt + question)

    try:
        response = openai.Completion.create(
            engine="text-davinci-001",
            prompt=prompt_s,
            temperature=0.7,
            max_tokens=64,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    except AuthenticationError as e:
        raise e
        
    relations = []
    if response:
        if response.choices and response.choices[0]:
            if "text" in response.choices[0]:
                lines = response.choices[0]["text"].replace("A: ", "").split('\n')
                relations = [line for line in lines if line]

    return relations


if __name__ == "__main__":

    pass

    # with open(DATABASE_FOLDER / 'gpt3_edges.json', 'r') as f:
    #     current_content = json.load(f)

    # with open(EVALUATION_FOLDER / 'green_eval_far_orig.yaml', 'r') as y:
    #     spec = yaml.load(y, Loader=yaml.SafeLoader)
    # mapping_spec = spec["mapping"]

    # engine = inflect.engine()
    # for mapping in tqdm(mapping_spec):
    #     i = mapping['input']
    #     for domain in ['base', 'target']:
    #         entities = i[domain]
    #         for direction in range(2):
    #             relations = get_entities_relations(entities[direction], entities[(direction+1)%2], engine)
    #             print(f"{entities[direction]}#{entities[(direction+1)%2]}")
    #             print(f"{relations}")
    #             print()