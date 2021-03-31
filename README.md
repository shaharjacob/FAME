# commonsense-analogy

## google engine
```bash
# using default example.yaml file without saving the results into a file
python google_engine.py

# using a config.yaml as a config file, and saving the results into out.csv
python google_engine.py -f config.yaml -o out.csv
```

## quasimodo
```bash
# Download the .tsv file in necessary: 
https://nextcloud.mpi-klsb.mpg.de/index.php/s/Sioq6rKP8LmjMDQ/download?path=%2FLatest&files=quasimodo43.tsv

# usage
from quasimodo import Quasimodo

# this will take time for saving all the oredered entries
# it will take time only on the first time, after that it will use the saved files
quasimodo = Quasimodo()
matches = quasimodo.get_subject_predicates('horse', 'cow')
print(matches)

# if you dont need the oredered entries, use the contructor like this:
quasimodo = Quasimodo(save_ordered=False)

# threshold (score that quasimodo gave) is by default 0.9, for change it use:
quasimodo = Quasimodo(score_threshold={new_threshold})
```


## references
**Quasimodo**: https://quasimodo.r2.enst.fr/  
**qa-srl**: http://qasrl.org/  
**hayadata-lab**: http://www.hyadatalab.com/  
