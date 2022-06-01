import re
import os
import json
import time
import inflect
from pathlib import Path

import openai
from openai.error import AuthenticationError

BACKEND_DIR = Path(__file__).resolve().parent.parent
EVALUATION_FOLDER = BACKEND_DIR / 'evaluation'
DATABASE_FOLDER = BACKEND_DIR / 'database'

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY= os.environ.get("OPENAI_API_KEY", "")
if 'CI' not in os.environ:
    openai.api_key = OPENAI_API_KEY

prompt = [
    "Q: What are the relations between blizzard and snowflake?",
    "A: A blizzard produces snowflakes.",
    "A: A blizzard contains a lot of snowflakes.",
    "",
    "Q: What are the relations between umbrella and rain?",
    "A: An umbrella protects from rain.",
    "A: An umbrella provides adequate protection from rain.",
    "",
    "Q: What are the relations between movie and screen?",
    "A: A movie displayed on a screen",
    "A: A movie can be shown on a screen",
    "",
    "Q: What are the relations between Newton and gravity?",
    "A: Newton discovered gravity.",
    "A: Newton invented gravity.",
    "",
    "Q: What are the relations between electron and nucleus?",
    "A: An electron revolves around the nucleus.",
    "A: An electron is much smaller than the nucleus.",
    "A: An electron attracts the nucleus.",
    "",
    "Q: What are the relations between water and pipe?",
    "A: Water flows through the pipe",
    "A: Water passes through the pipe",
    "",
    "Q: What are the relations between electron and wall?",
    "A: None",
    "",
    "Q: What are the relations between water and basketball?",
    "A: None"
    ""
]

def get_entities_relations(entity1: str, entity2: str, engine: inflect.engine):
    db_file = DATABASE_FOLDER / 'gpt3_edges.json'
    with open(db_file, 'r') as f:
        content = json.load(f)

    should_save = False
    if f"{entity1}#{entity2}" not in content:
        content[f"{entity1}#{entity2}"] = get_entities_relations_api(entity1, entity2)
        should_save = True
        time.sleep(1)

    if f"{entity2}#{entity1}" not in content:
        content[f"{entity2}#{entity1}"] = get_entities_relations_api(entity2, entity1)
        should_save = True
        time.sleep(1)

    if should_save:
        with open(db_file, 'w') as fw:
            json.dump(content, fw, indent='\t')

    relation_as_set = set()
    relations = list(set(content[f"{entity1}#{entity2}"] + content[f"{entity2}#{entity1}"]))
    # relations = list(set(content[f"{entity1}#{entity2}"]))
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
            _entity2 = engine.plural(entity2)
            match = re.search(f'{entity1} (.*?) {_entity2}', relation)
            if match:
                relation = match.group(1).strip()
                if relation:
                    relation_as_set.add(relation)
            else:
                _entity1 = engine.plural(entity1)
                match = re.search(f'{_entity1} (.*?) {entity2}', relation)
                if match:
                    relation = match.group(1).strip()
                    if relation:
                        relation_as_set.add(relation)
    
    return sorted(list(relation_as_set))



def get_entities_relations_api(entity1: str, entity2: str):
    question = [f"Q: What are the relations between {entity1} and {entity2}?"]
    prompt_s =  "\n".join(prompt + question)
    response = None
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
        print(f"{e}")
        
    relations = []
    if response:
        if response.choices and response.choices[0]:
            if "text" in response.choices[0]:
                lines = response.choices[0]["text"].replace("A: ", "").split('\n')
                relations = []
                for line in lines:
                    if line:
                        if line not in ['None', 'A:']:
                            if line.startswith("Q:"):
                                break
                            relations.append(line)

                relations = [line for line in lines if line and line != 'None' and line]

    return relations


if __name__ == "__main__":
    get_entities_relations_api("water tower", "hydrodynamics")