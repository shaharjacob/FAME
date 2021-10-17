import os
from typing import List
from pathlib import Path

import yaml
import click
from click import secho

import torch
from quasimodo import Quasimodo
from frequency import Frequencies
from mapping import beam_search_wrapper, mapping_wrapper, Solution, FREQUENCY_THRESHOLD


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
             threshold: float, 
             path: str, 
             specify: int, 
             freq_path: str, 
             algorithm: str,
             suggestions: bool = False):
    
    with open(TEST_FOLDER / path, 'r') as y:
        spec = yaml.load(y, Loader=yaml.SafeLoader)
    mapping_spec = spec["mapping"]
    results = Results()
    quasimodo = Quasimodo()
    freq_json_folder = f'jsons/merged/20%'
    path_for_json = f'{freq_json_folder}/{freq_path}'
    freq = Frequencies(path_for_json, threshold=threshold)
    for i, tv in enumerate(mapping_spec):
        if specify and i + 1 not in specify:
            continue
        
        if algorithm == 'beam':
            solutions = beam_search_wrapper(
                                            base=tv["input"]["base"], 
                                            target=tv["input"]["target"], 
                                            suggestions=suggestions, 
                                            N=20, 
                                            verbose=True, 
                                            quasimodo=quasimodo, 
                                            freq=freq, 
                                            model_name=model_name,
                                            threshold=threshold
                                        )
        elif algorithm == 'dfs':
            solutions = mapping_wrapper(
                                            base=tv["input"]["base"], 
                                            target=tv["input"]["target"], 
                                            suggestions=suggestions, 
                                            depth=tv["input"]["depth"], 
                                            top_n=5, 
                                            verbose=True, 
                                            quasimodo=quasimodo, 
                                            freq=freq, 
                                            model_name=model_name,
                                            threshold=threshold
                                        )
        else:
            secho("[ERROR] unsupported algorithm. (supported are 'beam' or 'dfs').")
            exit(1)
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
    print(f'{COLORS["OKGREEN"]}Total: {results.correct_answers}/{results.total_maps}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total (anywhere): {results.correct_anywhere}/{results.total_maps}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total correct from active mapping: {results.correct_answers}/{results.total_guesses}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total full mappings: {results.total_full_maps_correct}/{results.total_full_maps}{COLORS["ENDC"]}')
    print(f'{COLORS["OKGREEN"]}Total full mappings from active: {results.total_full_maps_correct}/{results.total_full_maps_from_active}{COLORS["ENDC"]}\n')


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
@click.option('-m', '--model', default="msmarco-distilbert-base-v4", type=str, help="The model for sBERT: https://huggingface.co/sentence-transformers")
@click.option('-t', '--threshold', default=FREQUENCY_THRESHOLD, type=float, help="Threshold for % to take from json frequencies")
@click.option('-y', '--yaml', default='validation.yaml', type=str, help="Path for the yaml for evaluation")
@click.option('-c', '--comment', default="", type=str, help="Additional comment for the job")
@click.option('-s', '--specify', default=[], type=int, multiple=True, help="Specify which entry of the yaml file to evaluate")
@click.option('-j', '--freq', default='all_1m_filter_3_sort.json', type=str, help="Which json to use for frequency file")
@click.option('-a', '--algo', default='dfs', type=str, help="Which algorithm to use")
@click.option('-g', '--suggestions', is_flag=True, help="Suggest entities if missing")
def run(model, threshold, yaml, comment, specify, freq, algo, suggestions):
    torch.cuda.empty_cache()
    evaluate(model, threshold, yaml, list(specify), freq, algo, suggestions)

if __name__ == '__main__':
    # os.environ['CI'] = 'true'
    run()