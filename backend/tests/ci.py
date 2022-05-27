import os
import sys
import unittest
from pathlib import Path

import yaml

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
from mapping.dfs import dfs_wrapper
from mapping.mapping import FREQUENCY_THRESHOLD
from mapping.beam_search import beam_search_wrapper
from mapping.quasimodo import Quasimodo, merge_tsvs
from mapping import concept_net, google_autosuggest


with open(backend_dir / 'tests' / 'tests.yaml', 'r') as y:
    spec = yaml.load(y, Loader=yaml.SafeLoader)

class TestFunctions(unittest.TestCase):

    if 'CI' in os.environ:
        merge_tsvs()
    quasimodo = Quasimodo(path=str(backend_dir / 'tsv' / 'merged' / 'quasimodo.tsv'))
    
    # def test_concept_net(self):
    #     for test in spec["concept_net_relations"]:
    #         reference = test['output']
    #         actual = concept_net.get_entities_relations(
    #             test["input"]["entities"][0], 
    #             test["input"]["entities"][1]
    #         )
    #         self.assertTrue(
    #             len(set(reference) - set(actual)) == 0, 
    #             f"sorted(reference)={sorted(reference)}, sorted(actual)={sorted(actual)}, Expect at least one to be matched"
    #         )

    def test_google_autosuggest_relations(self):
        # the return values changed all the time, so we just check the API is not broken.
        for test in spec["google_autosuggest_relations"]:
            reference = test["output"]
            actual = google_autosuggest.get_entities_relations(
                test["input"]["entities"][0], 
                test["input"]["entities"][1]
            ).get("props", [])
            self.assertTrue(
                len(set(reference) & set(actual)) > 0, 
                f"sorted(reference)={sorted(reference)}, sorted(actual)={sorted(actual)}, Expect at least one to be matched"
            )
    
    def test_google_autosuggest_suggestions(self):
        # the return values changed all the time, so we just check the API is not broken.
        for test in spec["google_autosuggest_suggestions"]:
            reference = test["output"]
            actual = google_autosuggest.get_entity_suggestions(
                test["input"]["entities"][0], 
                test["input"]["entities"][1]
            )
            
            self.assertTrue(
                len(set(reference) & set(actual)) > 0, 
                f"sorted(reference)={sorted(reference)}, sorted(actual)={sorted(actual)}, Expect at least one to be matched"
            )


    def test_quasimodo_props(self):  
        for test in spec["quasimodo_props"]:
            reference = test["output"]
            actual = [
                f"{prop[0]} {prop[1]}" 
                for prop in self.quasimodo.get_entity_props(
                    entity=test["input"]["entities"][0], 
                    n_largest=test["input"]["n_largest"], 
                    plural_and_singular=test["input"]["plural_and_singular"]
                )
            ]
            self.assertEqual(
                sorted(reference),
                sorted(actual),
                f"sorted(reference)={sorted(reference)} != sorted(actual)={sorted(actual)}"
            )
    

    def test_quasimodo_relations(self):
        for test in spec["quasimodo_relations"]:
            reference = test["output"]
            actual = self.quasimodo.get_entities_relations(
                entity1=test["input"]["entities"][0], 
                entity2=test["input"]["entities"][1], 
                n_largest=test["input"]["n_largest"], 
                plural_and_singular=test["input"]["plural_and_singular"]
            )
            self.assertEqual(
                sorted(reference), 
                sorted(actual),
                f"sorted(reference)={sorted(reference)} != sorted(actual)={sorted(actual)}"
            )
    

    def test_quasimodo_similarity_between_entities(self):
        for test in spec["quasimodo_similarity_between_entities"]:
            reference = test["output"]
            actual = [
                f"{prop[0]} {prop[1]}" 
                for prop in self.quasimodo.get_similarity_between_entities(
                    entity1=test["input"]["entities"][0], 
                    entity2=test["input"]["entities"][1], 
                    n_largest=test["input"]["n_largest"], 
                    plural_and_singular=test["input"]["plural_and_singular"]
                )
            ]
            self.assertEqual(
                sorted(reference), 
                sorted(actual),
                f"sorted(reference)={sorted(reference)} != sorted(actual)={sorted(actual)}"
            )


class TestMappingNoSuggestoins(unittest.TestCase):

    def test_without_suggestions(self):
        mapping_spec = spec["mapping"]
        for tv in mapping_spec:
            if tv["ignore"]:
                continue
            
            args = {
                "num_of_suggestions": 0,
                "N": tv["input"]["depth"],
                "verbose": True,
                "freq_th": FREQUENCY_THRESHOLD,
                "model_name": 'msmarco-distilbert-base-v4',
                "google": tv["input"]["google"],
                "openie": tv["input"]["openie"],
                "quasimodo": tv["input"]["quasimodo"],
                "conceptnet": tv["input"]["conceptnet"],
                "gpt3": tv["input"]["gpt3"]
            }

            algo_wrapper = beam_search_wrapper if tv['input']['algo'] == 'beam' else dfs_wrapper
            solutions = algo_wrapper(
                base=tv["input"]["base"], 
                target=tv["input"]["target"],
                args=args
            )
            solution = solutions[0]

            # check the mapping
            actual = solution.mapping
            reference = tv["output"]["mapping"]
            self.assertEqual(reference, actual)

            # check the score
            actual = solution.score
            reference = tv["output"]["score"]
            self.assertEqual(round(reference, 3), round(actual, 3), f'base={tv["input"]["base"]}, target={tv["input"]["target"]}')

class TestMappingSuggestoins(unittest.TestCase):

    def test_suggestoins(self):
        mapping_spec = spec["suggestions"]
        for tv in mapping_spec:
            if tv["ignore"]:
                continue
            
            args = {
                "num_of_suggestions": tv['input']['num_of_suggestions'],
                "N": tv['input']['depth'],
                "verbose": False if 'CI' in os.environ else True,
                "freq_th": FREQUENCY_THRESHOLD,
                "model_name": 'msmarco-distilbert-base-v4',
                "google": tv['input']['google'],
                "openie": tv['input']['openie'],
                "quasimodo": tv['input']['quasimodo'],
                "gpt3": tv['input']['gpt3'],
                "conceptnet": tv['input']['conceptnet'],
            }

            algo_wrapper = beam_search_wrapper if tv['input']['algo'] == 'beam' else dfs_wrapper
            solutions = algo_wrapper(
                base=tv["input"]["base"], 
                target=tv["input"]["target"],
                args=args
            )
            solution = solutions[tv["input"]["solution_rank"] - 1]

            # check the mapping
            actual = solution.mapping
            reference = tv["output"]["mapping"]
            self.assertEqual(reference, actual, tv['input'])

            # check the suggestions
            actual = solution.top_suggestions
            reference = tv["output"]["suggestions"]
            self.assertEqual(reference, actual, tv['input'])


if __name__ == '__main__':
    # os.environ['CI'] = 'true'
    unittest.main()