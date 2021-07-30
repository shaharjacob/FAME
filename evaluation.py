from pathlib import Path

import yaml
from click import secho

from mapping import mapping_wrapper


TEST_FOLDER = Path('tests')

def evaluate():
    with open(TEST_FOLDER / 'evaluate.yaml', 'r') as y:
        spec = yaml.load(y, Loader=yaml.SafeLoader)
    mapping_spec = spec["mapping"]
    total_good = 0
    total_maps = 0
    for tv in mapping_spec:

        solutions = mapping_wrapper(base=tv["input"]["base"], target=tv["input"]["target"], suggestions=False, depth=tv["input"]["depth"], top_n=10, verbose=True)
        if solutions:    
            solution = solutions[0]
            current_good = 0
            current_maps = 0

            # check the mapping
            actual = sorted(solution["mapping"])
            reference = sorted(tv["output"]["mapping"])
            for mapping in reference:
                if mapping in actual:
                    current_good += 1
                current_maps += 1
        else:
            current_maps = len(tv["output"]["mapping"])
                
        total_good += current_good
        total_maps += current_maps
        
        secho(f'Base: {tv["input"]["base"]}', fg="blue")
        secho(f'Target: {tv["input"]["target"]}', fg="blue")
        secho(f'Correct answers: {current_good}/{current_maps}\n', fg="cyan")
    secho(f'Total: {total_good}/{total_maps}\n', fg="green")


if __name__ == '__main__':
    evaluate()