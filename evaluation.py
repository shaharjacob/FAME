from typing import List
from pathlib import Path

import yaml
from click import secho

from mapping import mapping_wrapper


TEST_FOLDER = Path('tests')
COLORS = {
    "HEADER": '\033[95m',
    "OKBLUE": '\033[94m',
    "OKCYAN": '\033[96m',
    "OKGREEN": '\033[92m',
    "WARNING": '\033[93m',
    "FAIL": '\033[91m',
    "ENDC": '\033[0m',
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m',
}

def get_scores(corrent_mapping: List[str], solutions: List[List[str]]):
    res = {
        "choosen_good": 0,
        "best_good": 0,
        "index_for_best": 0,
    }
    
    for i, solution in enumerate(solutions):
        current_good = 0
        actual = sorted(solution["mapping"])
        reference = sorted(corrent_mapping)
        for mapping in reference:
            if mapping in actual:
                current_good += 1
        if current_good > res["best_good"]:
            res["best_good"] = current_good
            res["index_for_best"] = i
        if i == 0:
            res["choosen_good"] = current_good
    
    return res


def evaluate():
    with open(TEST_FOLDER / 'evaluate.yaml', 'r') as y:
        spec = yaml.load(y, Loader=yaml.SafeLoader)
    mapping_spec = spec["mapping"]
    total_good = 0
    total_anywhere = 0
    total_maps = 0
    for tv in mapping_spec:
        solutions = mapping_wrapper(base=tv["input"]["base"], target=tv["input"]["target"], suggestions=False, depth=tv["input"]["depth"], top_n=10, verbose=True)
        choosen_good = 0
        best_good = 0
        idx_best_good = -1
        current_maps = len(tv["output"]["mapping"])
        if solutions:
            res = get_scores(tv["output"]["mapping"], solutions)
            choosen_good = res["choosen_good"] # the map with the highest score
            best_good = res["best_good"] # the map that give maximum match with the correct mapping
            idx_best_good = res["index_for_best"]
            
        total_good += choosen_good
        total_anywhere += best_good
        total_maps += current_maps
        
        print(f'{COLORS["OKBLUE"]}Base: {tv["input"]["base"]}{COLORS["ENDC"]}')
        print(f'{COLORS["OKBLUE"]}Target: {tv["input"]["target"]}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Correct answers: {choosen_good}/{current_maps}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Anywhere in the solutions (#{idx_best_good+1}): {best_good}/{current_maps}{COLORS["ENDC"]}\n')
        # secho(f'Base: {tv["input"]["base"]}', fg="blue")
        # secho(f'Target: {tv["input"]["target"]}', fg="blue")
        # secho(f'Correct answers: {choosen_good}/{current_maps}', fg="cyan")
        # secho(f'Anywhere in the solutions (#{idx_best_good+1}): {best_good}/{current_maps}\n', fg="cyan")
        print("------------------------------------------------------------")
        print()
    print(f'{COLORS["OKGREEN"]}Total: {total_good}/{total_maps}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total (anywhere): {total_anywhere}/{total_maps}{COLORS["ENDC"]}\n')


if __name__ == '__main__':
    evaluate()