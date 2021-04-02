# commonsense-analogy

## Goal
Our main goal is to understand analogy, for example:  
windscreen wiper is used to remove water from the window like ...  
So first we need to understand the windscreen wiper rule.  
  
**The goal: understading nouns rules.**  
For example: a windscreen wiper is used to remove rain, snow and so.  
How to do it?  
  
**option 1: Wikifier**  
Accessing the first paragraph of the object in wikipedia.  
Give it to Wikifier.  
Looking for key-words like 'used to', and extract the relevant information from that area.  
  
**option 2: google-autocomplete**  
Using templates like:  
why do horses "*" stables  
The problem is there are no much information, and the results are not always what we looking for.  
  
**option 3: quasimodo**  
A lot of information, so we can extract the relevent for us.  
But also here, the information is not always what we looking for, sinse they worked with specific questions.  


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


## references
**Quasimodo**: https://quasimodo.r2.enst.fr/  
**qa-srl**: http://qasrl.org/  
**hayadata-lab**: http://www.hyadatalab.com/  

## Analogy datasets
**metamia**: http://www.metamia.com/