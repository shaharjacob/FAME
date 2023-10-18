import json
import yaml
import openai
import random
from pathlib import Path

openai.api_key = "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"

current_dir = Path(__file__).resolve().parent
evaluation_folder = current_dir.parent

def create_prompt(b1: str, b2: str, b3: str, t1: str, t2: str, t3: str):
    return "\n".join([
        "Q: Find an analogical mapping between the entities “eraser”, “paper” and “pencil” and the entities “keyboard”, “delete” and “screen”.",
        "A: eraser:pencil:paper::delete:keyboard:screen",
        "",
        "Q: Find an analogical mapping between the entities “captain” and “ship” and the entities “airplane” and “pilot”.",
        "A: captain:ship::pilot:airplane",
        "",
        "Q: Find an analogical mapping between the entities “feet” and “socks” and the entities “hands” and “gloves”.",
        "A: feet:socks::hands:gloves",
        "",
        "Q: Find an analogical mapping between the entities “language”, “word”, “letter” and “sentence” and the entities “digit”, “equation”, “math” and “number”.",
        "A: letter:word:sentence:language::digit:number:equation:math",
        "",
        f"Q: Find an analogical mapping between the entities “{b1}”, “{b2}” and “{b3}” and the entities “{t1}”, “{t2}” and “{t3}”.",
        "A:"
    ])


def create_prompt_arrows(b1: str, b2: str, b3: str, t1: str, t2: str, t3: str):
    return "\n".join([
        "Q: Find an analogical mapping between the entities “eraser”, “paper” and “pencil” and the entities “keyboard”, “delete” and “screen”.",
        "A: eraser -> delete, pencil -> keyboard, paper -> screen",
        "",
        "Q: Find an analogical mapping between the entities “captain” and “ship” and the entities “airplane” and “pilot”.",
        "A: captain -> pilot, ship -> airplane",
        "",
        "Q: Find an analogical mapping between the entities “feet” and “socks” and the entities “hands” and “gloves”.",
        "A: feet -> socks, hands -> gloves",
        "",
        "Q: Find an analogical mapping between the entities “language”, “word”, “letter” and “sentence” and the entities “digit”, “equation”, “math” and “number”.",
        "A: letter -> digit, word -> number, sentence -> equation, language -> math",
        "",
        f"Q: Find an analogical mapping between the entities “{b1}”, “{b2}” and “{b3}” and the entities “{t1}”, “{t2}” and “{t3}”.",
        "A:"
    ])


def gpt_predict(b1: str, b2: str, b3: str, t1: str, t2: str, t3: str, arrows: bool):
    prompt = create_prompt_arrows if arrows else create_prompt
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt(b1, b2, b3, t1, t2, t3),
        temperature=0.7,
        max_tokens=64,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response["choices"][0]["text"].strip()

def run(arrows: bool = False):
    with open(evaluation_folder / 'testset.yaml', 'r') as f:
        inputs = yaml.load(f, Loader=yaml.SafeLoader)["mapping"]

    for i in inputs:
        base = i["input"]["base"]
        target = i["input"]["target"]
        if len(base) != 3:
            continue
        random.shuffle(base)
        random.shuffle(target)

        res = gpt_predict(base[0], base[1], base[2], target[0], target[1], target[2], arrows=arrows)
        print(res)
        try:
            if arrows:
                print("\n".join([e.strip() for e in res.split(",")]))
            else:
                base_res, target_res = res.split("::")
                base_res_1, base_res_2, base_res_3 = base_res.split(":")
                target_res_1, target_res_2, target_res_3 = target_res.split(":")
                print(f"{base_res_1} --> {target_res_1}")
                print(f"{base_res_2} --> {target_res_2}")
                print(f"{base_res_3} --> {target_res_3}")
            print()
        except:
            print()

run(arrows=True)