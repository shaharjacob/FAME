# commonsense-analogy

## Goal
Our main goal is to understand analogy, for example:  
  
**1) DNA replication ~ a train track**  
The DNA is like a train track that gets pulled apart by the train.  
http://www.metamia.com/critique-dna-replication-like-a-train-track-1345  
  
**2) paragraph ~ a family**  
A paragraph is like a family. In a family, all the members are related. In a paragraph, all the sentences are related.  
http://www.metamia.com/critique-paragraph-like-family-6055  
  
## Why ?
Because sometimes it's much easier to explain something using an analogy.  

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

# so the output will be:
{'help:us', 'eat:grass', 'has_property:useful'}
```

```bash
# if you dont need the oredered entries, use the contructor like this:
quasimodo = Quasimodo(save_ordered=False)

# threshold (score that quasimodo gave) is by default 0.9, for change it use:
quasimodo = Quasimodo(score_threshold={new_threshold})
```

## metamia randomizer
```bash
# this site has a lot of complex analogy (http://www.metamia.com)
# a list of all the analogy isn't available (or dataset), but there is a page which
# return a random analogy (http://www.metamia.com/randomly-sample-the-analogy-database).
# so the script is iterate this page and parsing the analogy.

# usage (-i is the number of iteration)
python metamia.py -i 100 -o out.csv
```


## references
**Quasimodo**: https://quasimodo.r2.enst.fr/  
**qa-srl**: http://qasrl.org/  
**hayadata-lab**: http://www.hyadatalab.com/  

## Analogy datasets
**metamia**: http://www.metamia.com/