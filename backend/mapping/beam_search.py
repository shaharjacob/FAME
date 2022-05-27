import copy
from pathlib import Path
from typing import List, Dict

from . import mapping
from .mapping import Solution, Cache, Unmutables
from .suggestions import mapping_suggestions_wrapper

root = Path(__file__).resolve().parent.parent.parent


def beam_search(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    cache: Dict[str, Cache],
    args: dict):

    curr_solutions = []
    for solution in solutions:
        # we will get the top-N pairs with the best score.
        best_results_for_current_iteration, modified_results = mapping.get_best_pair_mapping_for_current_iteration(solution.availables, solution.sorted_results, args["N"])
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
                if relations_as_tuple in cache["relations"]:
                    continue
                cache["relations"].add(relations_as_tuple)

                solution_copy.scores.append(round(result["best_score"], 3))
                solution_copy.coverage.append(result["coverage"])

                # the new map that we found is b1:b2~t1:t2
                b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
                t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
                score = 0
                if b1 not in solution_copy.actual_base and t1 not in solution_copy.actual_target:
                    score += mapping.get_score(solution_copy.actual_base, solution_copy.actual_target, b1, t1, cache["scores"])
                    mapping.update_already_mapping(b1, t1, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

                if b2 not in solution_copy.actual_base and t2 not in solution_copy.actual_target:
                    score += mapping.get_score(solution_copy.actual_base, solution_copy.actual_target, b2, t2, cache["scores"])
                    mapping.update_already_mapping(b2, t2, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

                solution_copy.score += score
                mapping_repr = [f"{b} --> {t}" for b, t in zip(solution_copy.actual_base, solution_copy.actual_target)]
                mapping_repr_as_tuple = tuple(sorted(mapping_repr))
                if mapping_repr_as_tuple in cache["mappings"]:
                    continue
                cache["mappings"].add(mapping_repr_as_tuple)

                solution_copy.mapping = mapping_repr

                # here we update the possible/available pairs.
                # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
                # pairs that already maps. in our example it can be one of the following:
                # (a->1, c->3) or (b->2, c->3).
                new_available_pairs = mapping.update_paris_map(solution_copy.availables, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
                solution_copy.availables = new_available_pairs
                solution_copy.length = len(solution_copy.actual_base)
                curr_solutions.append(solution_copy)

    if not curr_solutions:
        return
    
    # this is the core of the beam search algorithm. We always keep with N solutions.
    solutions_ = sorted(solutions + curr_solutions, key=lambda x: (x.length, x.score), reverse=True)[:args["N"]]
    for i, solution_ in enumerate(solutions_):
        solutions[i] = solution_

    beam_search(
        base=base, 
        target=target,
        solutions=solutions,
        cache=cache,
        args=args
    )


def beam_search_wrapper(
    base: List[str], 
    target: List[str],
    args: dict,
    unmutables: Dict[str, Unmutables] = {}
    ) -> List[Solution]:

    # we want all the possible pairs.
    # general there are (n choose 2) * (n choose 2) * 2 pairs.
    available_pairs = mapping.get_all_possible_pairs_map(base, target)

    # better to init all the objects here, since they are not changed in the run
    mapping.set_unmutables(unmutables, args)

    cache = {"scores": {}, "mappings": set(), "relations": set()}
    best_results = mapping.get_best_pair_mapping(unmutables, available_pairs, cache)

    if args.get("use_base_mapping", False):
        actual_base = [v.split('-->')[0].strip() for v in args["use_base_mapping"]]
        actual_target = [v.split('-->')[1].strip() for v in args["use_base_mapping"]]
        solutions = [
            Solution(
                mapping=args["use_base_mapping"], 
                relations=[], 
                scores=[], 
                score=0, 
                actual_base=actual_base, 
                actual_target=actual_target, 
                actual_indecies={
                    'base': {
                        b: i for i,b in enumerate(actual_base)
                    }, 
                    'target': {
                        t: i for i,t in enumerate(actual_target)
                    }
                }, 
                length=len(actual_base),
                coverage=[],
                availables=copy.deepcopy(available_pairs),
                sorted_results=copy.deepcopy(best_results)
            ) 
        ]
    else:
        # this is an array of solutions we going to update in the mapping function.
        solutions = [
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
            for _ in range(args["N"])
        ]

        beam_search(base=base, 
                    target=target, 
                    solutions=solutions,
                    cache=cache, 
                    args=args)
    
    suggestions_solutions = mapping_suggestions_wrapper(base, 
                                                        target,
                                                        solutions,
                                                        args,
                                                        unmutables,
                                                        cache)

    all_solutions = sorted(solutions + suggestions_solutions, key=lambda x: (x.length, x.score), reverse=True)
    solutions_to_return_and_print = 10
    all_solutions = all_solutions[:solutions_to_return_and_print]
    if args["verbose"]:
        mapping.print_results(base, target, all_solutions)       

    return all_solutions