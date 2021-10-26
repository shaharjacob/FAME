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


def beam_search(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    freq: Frequencies,
    cache: dict,
    N: int = 4):

    curr_solutions = []
    for solution in solutions:
        # we will get the top-depth pairs with the best score.
        best_results_for_current_iteration, modified_results = get_best_pair_mapping_for_current_iteration(solution.availables, solution.sorted_results, N)
        solution.sorted_results = modified_results
        for result in best_results_for_current_iteration:
            # if the best score is > 0, we will update the base and target lists of the already mapping entities.
            # otherwise, if the best score is 0, we have no more mappings to do.
            if result["best_score"] > 0:
                solution_copy = copy.deepcopy(solution)
                
                solution_copy.relations.append(result["best_mapping"])
                relations_as_tuple = tuple([tuple(relation) for relation in sorted(solution_copy.relations)])
                if relations_as_tuple in relations_already_seen:
                    continue
                relations_already_seen.add(relations_as_tuple)

                solution_copy.scores.append(round(result["best_score"], 3))
                solution_copy.coverage.append(result["coverage"])

                b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
                t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
                score = 0
                if b1 not in solution_copy.actual_base and t1 not in solution_copy.actual_target:
                    score += get_score(solution_copy.actual_base, solution_copy.actual_target, b1, t1, cache)
                    update_already_mapping(b1, t1, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

                if b2 not in solution_copy.actual_base and t2 not in solution_copy.actual_target:
                    score += get_score(solution_copy.actual_base, solution_copy.actual_target, b2, t2, cache)
                    update_already_mapping(b2, t2, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

                solution_copy.score += score
                mapping_repr = [f"{b} --> {t}" for b, t in zip(solution_copy.actual_base, solution_copy.actual_target)]
                mapping_repr_as_tuple = tuple(sorted(mapping_repr))
                if mapping_repr_as_tuple in mappings_already_seen:
                    continue
                mappings_already_seen.add(mapping_repr_as_tuple)

                solution_copy.mapping = mapping_repr

                # here we update the possible/available pairs.
                # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
                # pairs that already maps. in our example it can be one of the following:
                # (a->1, c->3) or (b->2, c->3).
                new_available_pairs = update_paris_map(solution_copy.availables, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
                solution_copy.availables = new_available_pairs
                solution_copy.length = len(solution_copy.actual_base)
                curr_solutions.append(solution_copy)

    if not curr_solutions:
        return
    
    solutions_ = sorted(solutions + curr_solutions, key=lambda x: (x.length, x.score), reverse=True)[:N]
    for i, solution_ in enumerate(solutions_):
        solutions[i] = solution_

    beam_search(
        base=base, 
        target=target,
        solutions=solutions,
        relations_already_seen=relations_already_seen,
        mappings_already_seen=mappings_already_seen,
        freq=freq,
        cache=cache,
        N=N
    )


def beam_search_wrapper(base: List[str], 
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

    # better to init all the objects here, since they are not changed in the run
    if not quasimodo:
        quasimodo = Quasimodo()
    data_collector = DataCollector(quasimodo=quasimodo)
    model = SentenceEmbedding(model=model_name, data_collector=data_collector)
    if not freq:
        json_folder = root / 'backend' / 'frequency'
        freq = Frequencies(json_folder / 'freq.json', threshold=threshold)

    cache = {}
    best_results = get_best_pair_mapping(model, freq, data_collector, available_pairs, cache)

    # this is an array of solutions we going to update in the mapping function.
    solutions = []
    for i in range(N):
        solutions.append(
            Solution(
                mapping=[], 
                relations=[], 
                scores=[], 
                score=0, 
                actual_base=[], 
                actual_target=[], 
                actual_indecies={'base': {}, 'target': {}}, 
                length=0,
                coverage=[],
                availables=copy.deepcopy(available_pairs),
                sorted_results=copy.deepcopy(best_results)
            )
        )

    mappings_already_seen = set()
    relations_already_seen = set()
    beam_search(base=base, 
                target=target, 
                solutions=solutions, 
                mappings_already_seen=mappings_already_seen,
                relations_already_seen=relations_already_seen,
                freq=freq, 
                cache=cache, 
                N=N)
    
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
                                            mappings_already_seen=mappings_already_seen,
                                            relations_already_seen=relations_already_seen,
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
                                            mappings_already_seen=mappings_already_seen,
                                            relations_already_seen=relations_already_seen,
                                            cache=cache, 
                                            num_of_suggestions=num_of_suggestions, 
                                            verbose=verbose)

    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: (x.length, x.score), reverse=True)
    if not all_solutions:
        if verbose:
            secho("No solution found")
        return []
    if verbose:
        secho(f"\nBase: {base}", fg="blue", bold=True)
        secho(f"Target: {target}\n", fg="blue", bold=True)
        for i, solution in enumerate(all_solutions[:10]):
            if solution.score == 0:
                break
            secho(f"#{i+1}", fg="blue", bold=True)
            solution.print_solution()

    return all_solutions