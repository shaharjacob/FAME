import os
from typing import List
from pathlib import Path

import yaml
import click
from click import secho

import torch
from quasimodo import Quasimodo
from frequency import Frequencies
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
        current_good_good = 0
        actual = sorted(solution["mapping"])
        reference = sorted(corrent_mapping)
        for mapping in reference:
            if mapping in actual:
                current_good += 1
        for mapping in actual:
            if mapping in reference:
                current_good_good += 1
        if current_good > res["best_good"]:
            res["best_good"] = current_good
            res["index_for_best"] = i
        if i == 0:
            res["choosen_good"] = current_good
            res["choosen_good_good"] = current_good_good
            res["choosen_good_good_total"] = len(actual)
    
    return res


def evaluate(model_name: str, threshold: float):
    with open(TEST_FOLDER / 'evaluate.yaml', 'r') as y:
        spec = yaml.load(y, Loader=yaml.SafeLoader)
    mapping_spec = spec["mapping"]
    total_good = 0
    total_anywhere = 0
    total_maps = 0
    total_good_good = 0
    total_good_good_total = 0
    quasimodo = Quasimodo()
    pass_for_json = 'jsons/merged/20%/ci.json' if 'CI' in os.environ else 'jsons/merged/20%/all_1m_filter_3_sort.json'
    freq = Frequencies(pass_for_json, threshold=threshold)
    for tv in mapping_spec:
        solutions = mapping_wrapper(
                                        base=tv["input"]["base"], 
                                        target=tv["input"]["target"], 
                                        suggestions=False, 
                                        depth=tv["input"]["depth"], 
                                        top_n=5, 
                                        verbose=True, 
                                        quasimodo=quasimodo, 
                                        freq=freq, 
                                        model_name=model_name,
                                        threshold=threshold
                                    )
        choosen_good = 0
        best_good = 0
        idx_best_good = -1
        choosen_good_good = 0
        choosen_good_good_total = 0
        current_maps = len(tv["output"]["mapping"])
        if solutions:
            res = get_scores(tv["output"]["mapping"], solutions)
            choosen_good = res["choosen_good"] # the map with the highest score
            best_good = res["best_good"] # the map that give maximum match with the correct mapping
            idx_best_good = res["index_for_best"]
            choosen_good_good = res["choosen_good_good"]
            choosen_good_good_total = res["choosen_good_good_total"]
            
        total_good += choosen_good
        total_anywhere += best_good
        total_maps += current_maps
        total_good_good += choosen_good_good
        total_good_good_total += choosen_good_good_total
        
        print(f'{COLORS["OKBLUE"]}Base: {tv["input"]["base"]}{COLORS["ENDC"]}')
        print(f'{COLORS["OKBLUE"]}Target: {tv["input"]["target"]}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Correct answers: {choosen_good}/{current_maps}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Anywhere in the solutions (#{idx_best_good+1}): {best_good}/{current_maps}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Correct from active mapping: {choosen_good_good}/{choosen_good_good_total}{COLORS["ENDC"]}\n')
        print("------------------------------------------------------------")
        print()
    print(f'{COLORS["OKGREEN"]}Total: {total_good}/{total_maps}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total (anywhere): {total_anywhere}/{total_maps}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total correct from active mapping: {total_good_good}/{total_good_good_total}{COLORS["ENDC"]}\n')


# 'msmarco-distilbert-base-v4'            #1 - 34
# 'paraphrase-MiniLM-L12-v2'              #2 - 33
# 'paraphrase-mpnet-base-v2'              #3 - 31
# 'paraphrase-distilroberta-base-v2'      #4 - 29
# 'msmarco-roberta-base-v3'               #5 - 28
# 'bert-base-nli-mean-tokens'             #6 - 27
# 'stsb-mpnet-base-v2'                    #7 - 26
# 'distilbert-base-nli-stsb-mean-tokens'  #8 - 25

# 'xlm-r-distilroberta-base-paraphrase-v1' --> to big
# 'paraphrase-xlm-r-multilingual-v1'       --> to big
# 'LaBSE'                                  --> to big

@click.command()
@click.option('--model', default="msmarco-distilbert-base-v4", type=str, help="The model for sBERT: https://huggingface.co/sentence-transformers")
@click.option('--threshold', default=200, type=float, help="Threshold for % to take from json frequencies")
@click.option('--comment', default="", type=str, help="Additional comment for the job")
def run(model, threshold, comment):
    torch.cuda.empty_cache()
    evaluate(model, threshold)

if __name__ == '__main__':
    run()