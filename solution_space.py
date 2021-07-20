from itertools import combinations
from typing import List, Dict, Tuple



def get_all_possible_pairs_map_(base: List[str], target: List[str]) -> List[List[Tuple[str, str]]]:
    # complexity: (n choose 2) * (n choose 2) * 2

    base_comb = list(combinations(base, 2))
    target_comb = list(combinations(target, 2))
    target_comb += [(val[1], val[0]) for val in target_comb]
    return [[(base_pair[0], base_pair[1]), (target_pair[0], target_pair[1])] for base_pair in base_comb for target_pair in target_comb]

def update_paris_map(pairs_map: List[List[List[Tuple[str, str]]]], 
                    base_already_mapping: List[str], 
                    target_already_mapping: List[str]
                    ) -> List[List[List[Tuple[str, str]]]]:
    new_pairs_map = []
    for mapping in pairs_map:

        if mapping[0][0] in base_already_mapping and mapping[0][1] in base_already_mapping:
            # we already map base1 and base2
            continue
        
        if mapping[0][0] in base_already_mapping:
            if mapping[1][0] != target_already_mapping[base_already_mapping.index(mapping[0][0])]:
                # the match of mapping that already mapped is not true (base1->target1)
                continue
        
        if mapping[0][1] in base_already_mapping:
            if mapping[1][1] != target_already_mapping[base_already_mapping.index(mapping[0][1])]:
                # the match of mapping that already mapped is not true (base2->target2)
                continue
        
        if mapping[1][0] in target_already_mapping and mapping[1][1] in target_already_mapping:
            # we already map target1 and target2
            continue

        if mapping[1][0] in target_already_mapping:
            if mapping[0][0] != base_already_mapping[target_already_mapping.index(mapping[1][0])]:
                # the match of mapping that already mapped is not true (base1->target1)
                # print("debug here 1")
                continue
        
        if mapping[1][1] in target_already_mapping:
            if mapping[0][1] != base_already_mapping[target_already_mapping.index(mapping[1][1])]:
                # the match of mapping that already mapped is not true (base2->target2)
                # print("debug here 2")
                continue
        
        new_pairs_map.append(mapping)
    return new_pairs_map

def update_list(already_mapping_list: List[str], 
                entities: Tuple[str, str]
                ) -> List[str]:
    if entities[0] not in already_mapping_list:
        already_mapping_list.append(entities[0])
    if entities[1] not in already_mapping_list:
        already_mapping_list.append(entities[1])
    return already_mapping_list



def validate_solution(solution: List[Tuple[str, str]]) -> bool:
    base_already_map = []
    target_already_map = []
    for single_map in solution:
        if single_map[0][0] in base_already_map and single_map[1][0] not in target_already_map:
            return False
        if single_map[0][0] not in base_already_map and single_map[1][0] in target_already_map:
            return False
        if single_map[0][1] in base_already_map and single_map[1][1] not in target_already_map:
            return False
        if single_map[0][1] not in base_already_map and single_map[1][1] in target_already_map:
            return False
        if single_map[0][0] in base_already_map and single_map[1][0] in target_already_map:
            if single_map[1][0] != target_already_map[base_already_map.index(single_map[0][0])]:
                return False
            if single_map[0][0] != base_already_map[target_already_map.index(single_map[1][0])]:
                return False
        if single_map[0][1] in base_already_map and single_map[1][1] in target_already_map:
            if single_map[1][1] != target_already_map[base_already_map.index(single_map[0][1])]:
                return False
            if single_map[0][1] != base_already_map[target_already_map.index(single_map[1][1])]:
                return False

        if single_map[0][0] not in base_already_map and single_map[1][0] not in target_already_map:
            base_already_map.append(single_map[0][0])
            target_already_map.append(single_map[1][0])

        if single_map[0][0] in base_already_map and single_map[1][0] not in target_already_map:
            return False
        if single_map[0][0] not in base_already_map and single_map[1][0] in target_already_map:
            return False
        if single_map[0][1] in base_already_map and single_map[1][1] not in target_already_map:
            return False
        if single_map[0][1] not in base_already_map and single_map[1][1] in target_already_map:
            return False
        if single_map[0][0] in base_already_map and single_map[1][0] in target_already_map:
            if single_map[1][0] != target_already_map[base_already_map.index(single_map[0][0])]:
                return False
            if single_map[0][0] != base_already_map[target_already_map.index(single_map[1][0])]:
                return False
        if single_map[0][1] in base_already_map and single_map[1][1] in target_already_map:
            if single_map[1][1] != target_already_map[base_already_map.index(single_map[0][1])]:
                return False
            if single_map[0][1] != base_already_map[target_already_map.index(single_map[1][1])]:
                return False


        if single_map[0][1] not in base_already_map and single_map[1][1] not in target_already_map:
            base_already_map.append(single_map[0][1])
            target_already_map.append(single_map[1][1])

    return len(base_already_map) == 6


def get_map(pairs: List[List[Tuple[str, str]]]) -> Tuple[str]:
    mapping = set()
    for pair in pairs:
        mapping.add(f"{pair[0][0]} --> {pair[1][0]}")
        mapping.add(f"{pair[0][1]} --> {pair[1][1]}")
    return tuple(sorted(list(mapping)))



import pickle
from click import secho

base = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6']
target = ['t1', 't2', 't3', 't4', 't5', 't6']
all_paris = get_all_possible_pairs_map_(base, target)
with open("pickle4", 'wb') as f:
    pickle.dump(all_paris, f)
combs = list(combinations(all_paris, 5))
goods = [comb for comb in combs if validate_solution(comb)]
print(len(goods))
with open("pickle3", 'wb') as f:
    pickle.dump(goods, f)

# with open('pickle2', 'rb') as f:
#     goods = pickle.load(f)

d = {}
for good in goods:
    mapping = get_map(list(good))
    d[mapping] = d.get(mapping, 0) + 1
    if mapping == ('b1 --> t1', 'b2 --> t2', 'b3 --> t3', 'b4 --> t4', 'b5 --> t5', 'b6 --> t6'):
        for pair in good:
            secho(f"{pair[0]},", nl=False)
        print()
print(d[('b1 --> t1', 'b2 --> t2', 'b3 --> t3', 'b4 --> t4', 'b5 --> t5', 'b6 --> t6')])
# print(len(d))
# for k,v in d.items():
#     print(f"{k}: {v}")

