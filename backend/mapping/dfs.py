import copy
from pathlib import Path
from typing import List, Dict

from . import mapping
from .mapping import Solution, Cache, Unmutables
from .suggestions import mapping_suggestions_wrapper

root = Path(__file__).resolve().parent.parent.parent


def dfs(
    base: List[str], 
    target: List[str],
    solutions: List[Solution],
    curr_solution: Solution,
    cache: Dict[str, Cache],
    args: dict):

    if curr_solution.actual_base:
        # first we will check if this node already seen in different variation
        relations_as_tuple = tuple([tuple(relation) for relation in sorted(curr_solution.relations)])
        if relations_as_tuple in cache["relations"]:
            return
        mapping_repr = [f"{b} --> {t}" for b, t in zip(curr_solution.actual_base, curr_solution.actual_target)]
        mapping_repr_as_tuple = tuple(sorted(mapping_repr))
        if mapping_repr_as_tuple in cache["mappings"]:
            return
        
        # the following sets using only for quick exists-check.
        cache["relations"].add(relations_as_tuple)
        cache["mappings"].add(mapping_repr_as_tuple)
        curr_solution.mapping = mapping_repr
        # new solution
        # in the end we will sort by the length and the score. So its ok to add all solutions
        solutions.append(curr_solution)

    # base case for recursive function. there is no more available pairs to match (base->target)
    if len(curr_solution.actual_base) == min(len(base), len(target)):
        return

    # we will get the top-depth pairs with the best score.
    best_results_for_current_iteration, modified_results = mapping.get_best_pair_mapping_for_current_iteration(curr_solution.availables, curr_solution.sorted_results, args["N"])
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
                score += mapping.get_score(solution_copy.actual_base, solution_copy.actual_target, b1, t1, cache["scores"])
                mapping.update_already_mapping(b1, t1, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)

            if b2 not in solution_copy.actual_base and t2 not in solution_copy.actual_target:
                score += mapping.get_score(solution_copy.actual_base, solution_copy.actual_target, b2, t2, cache["scores"])
                mapping.update_already_mapping(b2, t2, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
            
            solution_copy.score += round(score, 3)
            
            # here we update the possible/available pairs.
            # for example, if we already map a->1, b->2, we will looking only for pairs which respect the 
            # pairs that already maps. in our example it can be one of the following:
            # (a->1, c->3) or (b->2, c->3).
            solution_copy.availables = mapping.update_paris_map(solution_copy.availables, solution_copy.actual_base, solution_copy.actual_target, solution_copy.actual_indecies)
            solution_copy.length = len(solution_copy.actual_base)
            solution_copy.sorted_results = modified_results
            
            dfs(
                base=base, 
                target=target,
                solutions=solutions,
                curr_solution=solution_copy,
                cache=cache,
                args=args
            )


def dfs_wrapper(
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
    
    # this is an array of solutions we going to update in the mapping function.
    solutions = []

    dfs(base=base, 
        target=target, 
        solutions=solutions,
        curr_solution=initial_solution,
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