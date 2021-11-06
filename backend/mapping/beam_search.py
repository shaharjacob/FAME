import copy
from pathlib import Path
from typing import List, Tuple, Union, Set

from .quasimodo import Quasimodo
from .data_collector import DataCollector
from frequency.frequency import Frequencies
from .suggestions import mapping_suggestions_wrapper
from utils.sentence_embadding import SentenceEmbedding
from .mapping import Solution, Pair
from .mapping import get_score, update_already_mapping, update_paris_map, get_best_pair_mapping_for_current_iteration, get_all_possible_pairs_map, get_best_pair_mapping, print_results

root = Path(__file__).resolve().parent.parent.parent


def beam_search(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    relations_already_seen: Set[Tuple[Tuple[Pair]]],
    mappings_already_seen: Set[Tuple[str]],
    freq: Frequencies,
    cache: dict,
    N: int):

    curr_solutions = []
    for solution in solutions:
        # we will get the top-N pairs with the best score.
        best_results_for_current_iteration, modified_results = get_best_pair_mapping_for_current_iteration(solution.availables, solution.sorted_results, N)
        solution.sorted_results = modified_results
        for result in best_results_for_current_iteration:
            # if the best score is > 0, we will update the base and target lists of the already mapping entities.
            # otherwise, if the best score is 0, we have no more mappings to do.
            if result["best_score"] > 0:
                # the current solution is our base for the new one. We need it but we don't want to affect him
                # by modified the new one, so we need that deepcopy.
                solution_copy = copy.deepcopy(solution)
                
                solution_copy.relations.append(result["best_mapping"])
                relations_as_tuple = tuple([tuple(relation) for relation in sorted(solution_copy.relations)])
                if relations_as_tuple in relations_already_seen:
                    continue
                relations_already_seen.add(relations_as_tuple)

                solution_copy.scores.append(round(result["best_score"], 3))
                solution_copy.coverage.append(result["coverage"])

                # the new map that we found is b1:b2~t1:t2
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
    
    # this is the core of the beam search algorithm. We always keep with N solutions.
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


def beam_search_wrapper(
    base: List[str], 
    target: List[str],
    num_of_suggestions: int,
    N: int, 
    verbose: bool,
    model_name: str,
    freq_th: Union[float, int]
    ) -> List[Solution]:

    # we want all the possible pairs.
    # general there are (n choose 2) * (n choose 2) * 2 pairs.
    available_pairs = get_all_possible_pairs_map(base, target)

    # better to init all the objects here, since they are not changed in the run
    quasimodo = Quasimodo()
    data_collector = DataCollector(quasimodo=quasimodo)
    model = SentenceEmbedding(model=model_name, data_collector=data_collector)
    json_folder = root / 'backend' / 'frequency'
    freq = Frequencies(json_folder / 'freq.json', threshold=freq_th)

    cache = {}
    best_results = get_best_pair_mapping(model, freq, data_collector, available_pairs, cache)

    # this is an array of solutions we going to update in the mapping function.
    solutions = [Solution(
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
                sorted_results=copy.deepcopy(best_results)) 
                for _ in range(N)]

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
    
    suggestions_solutions = mapping_suggestions_wrapper(base, 
                                                        target,
                                                        num_of_suggestions,
                                                        solutions,
                                                        data_collector,
                                                        model,
                                                        freq,
                                                        mappings_already_seen,
                                                        relations_already_seen,
                                                        cache,
                                                        verbose)

    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: (x.length, x.score), reverse=True)
    solutions_to_return_and_print = 10
    all_solutions = all_solutions[:solutions_to_return_and_print]
    if verbose:
        print_results(base, target, all_solutions)       

    return all_solutions