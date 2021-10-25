import os
import copy
from pathlib import Path
from typing import List, Tuple, Union, Set

from click import secho

from .quasimodo import Quasimodo
from .data_collector import DataCollector
from frequency.frequency import Frequencies
from .suggestions import mapping_suggestions_wrapper
from utils.sentence_embadding import SentenceEmbedding
from .mapping import Solution, Pair, FREQUENCY_THRESHOLD
from .mapping import get_score, update_already_mapping, update_paris_map, get_best_pair_mapping_for_current_iteration, get_all_possible_pairs_map, get_best_pair_mapping

root = Path(__file__).resolve().parent.parent.parent


def dfs(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    freq: Frequencies,
    curr_solution: Solution,
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    cache: dict,
    calls: List[int], # debug
    depth: int = 2):

    calls[0] += 1 # just to print the total recursive calls
    if curr_solution.actual_base:
        # first we will check if this node already seen in different variation
        relations_as_tuple = tuple([tuple(relation) for relation in sorted(curr_solution.relations)])
        if relations_as_tuple in relations_already_seen:
            return
        mapping_repr = [f"{b} --> {t}" for b, t in zip(curr_solution.actual_base, curr_solution.actual_target)]
        mapping_repr_as_tuple = tuple(sorted(mapping_repr))
        if mapping_repr_as_tuple in mappings_already_seen:
            return
        
        # the following sets using only for quick exists-check.
        relations_already_seen.add(relations_as_tuple)
        mappings_already_seen.add(mapping_repr_as_tuple)
        curr_solution.mapping = mapping_repr
        # new solution
        # in the end we will sort by the length and the score. So its ok to add all solutions
        solutions.append(curr_solution)

    # base case for recursive function. there is no more available pairs to match (base->target)
    if len(curr_solution.actual_base) == min(len(base), len(target)):
        return

    # we will get the top-depth pairs with the best score.
    best_results_for_current_iteration, modified_results = get_best_pair_mapping_for_current_iteration(curr_solution.availables, curr_solution.sorted_results, depth)
    for result in best_results_for_current_iteration:
        # if the best score is > 0, we will update the base and target lists of the already mapping entities.
        # otherwise, if the best score is 0, we have no more mappings to do.
        if result["best_score"] > 0:
            # deepcopy is more safe when working with recursive functions
            solution_copy = copy.deepcopy(curr_solution)
            solution_copy.relations.append(result["best_mapping"])
            solution_copy.scores.append(round(result["best_score"], 3))
            solution_copy.coverage.append(result["coverage"])

            # we will add the new mapping to the already mapping lists. They must be in the same shape.
            b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
            t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
            score = 0
            if b1 not in solution_copy.actual_base and t1 not in solution_copy.actual_target:
                score += get_score(solution_copy.actual_base, solution_copy.actual_target, b1, t1, cache)
                update_already_mapping(b1, t1, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

            if b2 not in solution_copy.actual_base and t2 not in solution_copy.actual_target:
                score += get_score(solution_copy.actual_base, solution_copy.actual_target, b2, t2, cache)
                update_already_mapping(b2, t2, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
            
            solution_copy.score += round(score, 3)
            
            # here we update the possible/available pairs.
            # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
            # pairs that already maps. in our example it can be one of the following:
            # (a->1, c->3) or (b->2, c->3).
            solution_copy.availables = update_paris_map(solution_copy.availables, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
            solution_copy.length = len(solution_copy.actual_base)
            solution_copy.sorted_results = modified_results
            
            dfs(
                base=base, 
                target=target,
                solutions=solutions,
                freq=freq,
                curr_solution=solution_copy,
                relations_already_seen=relations_already_seen,
                mappings_already_seen=mappings_already_seen,
                cache=cache,
                calls=calls,
                depth=depth
            )


def dfs_wrapper(base: List[str], 
                target: List[str], 
                suggestions: bool = False, 
                num_of_suggestions: int = 1,
                N: int = 4,
                verbose: bool = False, 
                quasimodo: Quasimodo = None, 
                freq: Frequencies = None, 
                model_name: str = 'msmarco-distilbert-base-v4',
                threshold: Union[float, int] = FREQUENCY_THRESHOLD
                ) -> List[Solution]:

    # we want all the possible pairs.
    # general there are (n choose 2) * (n choose 2) * 2 pairs.
    available_pairs = get_all_possible_pairs_map(base, target)

    # this is an array of solutions we going to update in the mapping function.
    solutions = []

    # better to init all the objects here, since they are not changed in the run
    if not quasimodo:
        quasimodo = Quasimodo()
    data_collector = DataCollector(quasimodo=quasimodo)
    model = SentenceEmbedding(model=model_name, data_collector=data_collector)
    if not freq:
        json_folder = root / 'backend' / 'frequency' /  'jsons' / 'merged' / '20%'
        json_basename = 'ci.json' if 'CI' in os.environ else 'all_1m_filter_3_sort.json'
        freq = Frequencies(json_folder / json_basename, threshold=threshold)

    cache = {}
    calls = [0]
    best_results = get_best_pair_mapping(model, freq, data_collector, available_pairs, cache)
    initial_solution = Solution(
                            mapping=[], 
                            relations=[], 
                            scores=[], 
                            score=0, 
                            actual_base=[], 
                            actual_target=[], 
                            actual_indecies={'base': {}, 'target': {}}, 
                            length=0,
                            coverage=[],
                            sorted_results=best_results,
                            availables=copy.deepcopy(available_pairs)
                        )
    
    mappings_already_seen = set()
    relations_already_seen = set()
    dfs(base=base, 
        target=target, 
        solutions=solutions, 
        freq=freq, 
        curr_solution=initial_solution,
        relations_already_seen=relations_already_seen, 
        mappings_already_seen=mappings_already_seen, 
        cache=cache, 
        calls=calls, 
        depth=N)

    # array of addition solutions for the suggestions if some entities have missing mappings.
    suggestions_solutions = []
    if suggestions and num_of_suggestions > 0:
        solutions = sorted(solutions, key=lambda x: (x.length, x.score), reverse=True)
        if solutions and solutions[0].length < max(len(base), len(target)):
            number_of_solutions_for_suggestions = 3
            # the idea is to iterate over the founded solutions, and check if there are entities are not mapped.
            for solution in solutions[:number_of_solutions_for_suggestions]:
                if solution.length < max(len(base), len(target)) - 1:
                    # this logic is checked only if ONE entity have missing mapping (from base or target)
                    continue
                
                mapping_suggestions_wrapper(domain=base, 
                                            first_domain="actual_base", 
                                            second_domain="actual_target", 
                                            solution=solution, 
                                            data_collector=data_collector, 
                                            model=model, 
                                            freq=freq, 
                                            solutions=suggestions_solutions, 
                                            relations_already_seen=relations_already_seen, 
                                            mappings_already_seen=mappings_already_seen, 
                                            cache=cache, 
                                            num_of_suggestions=num_of_suggestions, 
                                            verbose=verbose)
                
                mapping_suggestions_wrapper(domain=target, 
                                            first_domain="actual_target", 
                                            second_domain="actual_base", 
                                            solution=solution, 
                                            data_collector=data_collector, 
                                            model=model, 
                                            freq=freq, 
                                            solutions=suggestions_solutions, 
                                            relations_already_seen=relations_already_seen, 
                                            mappings_already_seen=mappings_already_seen, 
                                            cache=cache, 
                                            num_of_suggestions=num_of_suggestions, 
                                            verbose=verbose)

    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: (x.length, x.score), reverse=True)
    if not all_solutions:
        if verbose:
            secho("No solution found")
        return []
    
    solutions_to_return_and_print = 10
    if verbose:
        secho(f"\nBase: {base}", fg="blue", bold=True)
        secho(f"Target: {target}\n", fg="blue", bold=True)
        for i, solution in enumerate(all_solutions[:solutions_to_return_and_print]):
            secho(f"#{i+1}", fg="blue", bold=True)
            solution.print_solution()

    secho(f"Number of recursive calls: {calls[0]}\n")
    return all_solutions[:solutions_to_return_and_print]