import os
import sys
from typing import List
from pathlib import Path

import yaml
import torch
import click
from click import secho

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))
from mapping.dfs import dfs_wrapper
from mapping.beam_search import beam_search_wrapper
from mapping.mapping import Solution, FREQUENCY_THRESHOLD, mapping_wrapper

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

class Result:
    def __init__(self):
        self.correct_answers = 0 # the map with the highest score
        self.num_of_guesses = 0
        self.num_of_maps = 0
        self.best = 0 # the map that give maximum match with the correct mapping
        self.best_idx = -1
        self.full_map = 0


class Results:
    def __init__(self):
        self.correct_answers = 0
        self.correct_anywhere = 0
        self.total_maps = 0
        self.total_guesses = 0
        self.total_full_maps_correct = 0
        self.total_full_maps = 0
        self.total_full_maps_from_active = 0
        
    
    def update_results(self, result: Result):
        self.correct_answers += result.correct_answers
        self.correct_anywhere += result.best
        self.total_maps += result.num_of_maps
        self.total_guesses += result.num_of_guesses
        self.total_full_maps_correct += result.full_map


def update_result(correct_mapping: List[str], solutions: List[Solution], result: Result):
    for i, solution in enumerate(solutions):
        current_good = 0
        actual = sorted(solution.mapping)
        reference = sorted(correct_mapping)
        for mapping in reference:
            if mapping in actual:
                current_good += 1
        if current_good > result.best:
            result.best = current_good
            result.best_idx = i
        if i == 0:
            result.correct_answers = current_good
            result.num_of_guesses = len(actual)
            if current_good == len(reference):
                result.full_map = 1
            
        

def evaluate(model_name: str, 
             freq_th: float, 
             path: str, 
             specify: int,
             algorithm: str,
             num_of_suggestions: int):
    
    if algorithm not in ['beam', 'dfs']:
            secho("[ERROR] unsupported algorithm. (supported are 'beam' or 'dfs').")
            exit(1)

    with open(current_dir / path, 'r') as y:
        spec = yaml.load(y, Loader=yaml.SafeLoader)
    mapping_spec = spec["mapping"]
    results = Results()

    for i, tv in enumerate(mapping_spec):
        if specify and i + 1 not in specify:
            continue

        args = {
            "num_of_suggestions": num_of_suggestions,
            "N": tv["input"]["depth"][algorithm],
            "verbose": True,
            "freq_th": freq_th,
            "model_name": model_name,
            "google": True,
            "openie": True,
            "quasimodo": True,
            "gpt3": True if 'CI' not in os.environ else False,
            "conceptnet": False,
            "use_base_mapping": tv["output"]["mapping"] if tv["input"].get("use_base_mapping", False) else []
        }

        algo_func = beam_search_wrapper if algorithm == 'beam' else dfs_wrapper
        solutions = mapping_wrapper(algo_func, 
                                    base=tv["input"]["base"], 
                                    target=tv["input"]["target"],
                                    args=args)
        result = Result()
        current_maps = len(tv["output"]["mapping"])
        result.num_of_maps = current_maps
        if solutions:
            update_result(tv["output"]["mapping"], solutions, result) 
            results.total_full_maps_from_active += 1
        results.update_results(result)
        results.total_full_maps += 1
        
        print(f'{COLORS["OKBLUE"]}Base: {tv["input"]["base"]}{COLORS["ENDC"]}')
        print(f'{COLORS["OKBLUE"]}Target: {tv["input"]["target"]}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Correct answers: {result.correct_answers}/{current_maps}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Anywhere in the solutions (#{result.best_idx+1}): {result.best}/{current_maps}{COLORS["ENDC"]}')
        print(f'{COLORS["OKGREEN"]}Correct from active mapping: {result.correct_answers}/{result.num_of_guesses}{COLORS["ENDC"]}\n')
        print("------------------------------------------------------------")
        print()
    
    if results.total_maps - results.correct_answers > 0:
        mistake_because_of_coverage = round(((results.total_maps - results.total_guesses) / (results.total_maps - results.correct_answers)) * 100, 1)
    else:
        mistake_because_of_coverage = 100
    mistake_because_of_coverage_string = ""
    if mistake_because_of_coverage > 0:
        mistake_because_of_coverage_string = f" ({mistake_because_of_coverage}% of the mistakes because of coverage)"
    success_pres = round((results.correct_answers / results.total_maps) * 100, 1)
    print(f'{COLORS["OKGREEN"]}Total: {results.correct_answers}/{results.total_maps} ({success_pres}%){mistake_because_of_coverage_string}{COLORS["ENDC"]}')
    
    # print(f'{COLORS["OKGREEN"]}Total (anywhere): {results.correct_anywhere}/{results.total_maps}{COLORS["ENDC"]}')
    
    if results.total_full_maps - results.total_full_maps_correct > 0:
        mistake_because_of_coverage = round(((results.total_full_maps - results.total_full_maps_from_active) / (results.total_full_maps - results.total_full_maps_correct)) * 100, 1)
    else:
        mistake_because_of_coverage = 100
    mistake_because_of_coverage_string = ""
    if mistake_because_of_coverage > 0:
        mistake_because_of_coverage_string = f" ({mistake_because_of_coverage}% of the mistakes because of coverage)"
    success_pres = round((results.total_full_maps_correct / results.total_full_maps) * 100, 1)
    print(f'{COLORS["OKGREEN"]}Total full mappings: {results.total_full_maps_correct}/{results.total_full_maps} ({success_pres}%){mistake_because_of_coverage_string}{COLORS["ENDC"]}')
    
    print()
    print(f'{COLORS["OKGREEN"]}Total correct from active mapping: {results.correct_answers}/{results.total_guesses}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total full mappings from active: {results.total_full_maps_correct}/{results.total_full_maps_from_active}{COLORS["ENDC"]}\n')


@click.command()
@click.option('-m', '--model', default="msmarco-distilbert-base-v4", type=str, help="The model for sBERT: https://huggingface.co/sentence-transformers")
@click.option('-t', '--freq-th', default=FREQUENCY_THRESHOLD, type=float, help="Threshold for % to take from json frequencies")
@click.option('-y', '--yaml', default='validation.yaml', type=str, help="Path for the yaml for evaluation")
@click.option('-c', '--comment', default="", type=str, help="Additional comment for the job")
@click.option('-s', '--specify', default=[], type=int, multiple=True, help="Specify which entry of the yaml file to evaluate")
@click.option('-a', '--algo', default='beam', type=str, help="Which algorithm to use")
@click.option('-g', '--num-of-suggestions', type=int, default=0, help="Number of suggestions for missing entities")
def run(model, freq_th, yaml, comment, specify, algo, num_of_suggestions):
    torch.cuda.empty_cache()
    evaluate(model, freq_th, yaml, list(specify), algo, num_of_suggestions)

if __name__ == '__main__':
    # os.environ['CI'] = 'true'
    run()