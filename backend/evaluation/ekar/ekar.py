import json
from pathlib import Path

import yaml

current_dir = Path(__file__).resolve().parent

def dump_for_evaluation():
    with open(current_dir / 'ekar_validation.json', 'r') as f:
        ekar_entries = json.load(f)

    answerKeys = {
        "A": 0,
        "B": 1,
        "C": 2,
        "D": 3
    }
    samples = []
    for ekar_entry in ekar_entries:
        for i, option in enumerate(ekar_entry["choices"]["text"]):
            samples.append({
                "base": ekar_entry["question"].split(":"),
                "target": option.split(":"),
                "depth": {
                    "beam": 20,
                    "dfs": 4
                },
                "ekar_answer": answerKeys[ekar_entry["answerKey"]] == i,
                "clean_nouns": ekar_entry["clean_nouns"]
            })

    with open(current_dir / 'ekar_english.json', 'w') as f2:
        json.dump(samples, f2, indent='\t')


def evaluate():
    with open(current_dir / 'ekar_results.json', 'r') as f:
        ekar_results = json.load(f)
    
    total, correct = 0, 0
    for i in range(0, len(ekar_results), 4):
        fame_answer = max(ekar_results[i:i+4], key=lambda x: x["score"])
        if fame_answer["ekar_answer"]:
            correct += 1
        total += 1
    
    success_pres = round((correct / total) * 100, 1)
    print(f'\033[92mTotal: {correct}/{total} ({success_pres}%)\033[0m')


def to_yaml(path: Path):
    entries = []
    with open(path, 'r') as f:
        entries = json.load(f)

    entries_for_yaml = []
    for i, entry in enumerate(entries):
        if entry["ekar_answer"]:
            entries_for_yaml.append({
                "input": {
                    "base": entry["base"],
                    "target": entry["target"],
                    "depth": entry["depth"] 
                },
                "output": {
                    "mapping": [f"{b} --> {t}" for b, t in zip(entry["base"], entry["target"])]
                },
                # "clean_nouns": entry["clean_nouns"],
                # "explanation": entry["explanation"],
                # "order": i+1
            })

    with open(current_dir / f"{path.stem}.yaml", 'w') as f2:
        yaml.dump({"mapping": entries_for_yaml }, f2, indent=4)



# dump_for_evaluation()
# compress_results()
# evaluate()
to_yaml(current_dir / "ekar_english_nouns_3x3.json")