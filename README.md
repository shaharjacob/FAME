# commonsense-analogy

## Goal
Our main goal is to understand analogy, for example:  

**1) Finding a good man is like finding a needle in a haystack:**  
As Dusty Springfield knows, finding a small needle in a pile of hay takes a long time, so the task at hand is likely to be hard and tedious.  
https://examples.yourdictionary.com/analogy-ex.html  
  
**2) That's as useful as rearranging deck chairs on the Titanic:**
 It looks like you're doing something helpful but really it will make no difference in the end.  
 https://examples.yourdictionary.com/analogy-ex.html  
  
**3) DNA replication ~ a train track**  
The DNA is like a train track that gets pulled apart by the train.  
http://www.metamia.com/critique-dna-replication-like-a-train-track-1345  
  
**4) paragraph ~ a family**  
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
- **Quasimodo**: https://quasimodo.r2.enst.fr/  
- **qa-srl**: http://qasrl.org/  
- **hayadata-lab**: http://www.hyadatalab.com/  

## Analogy datasets
- **metamia**: http://www.metamia.com/
- **Vecto**: https://vecto.space/
  
## PDFs
**Analogy-based Detection of Morphological and Semantic Relations With Word Embeddings: What Works and What Doesn’t**:  
- https://www.aclweb.org/anthology/N16-2002.pdf

**Using Analogy To Acquire CommonsenseKnowledge from Human Contributors**:  
- https://dspace.mit.edu/handle/1721.1/87342  
  
**Reasoning and Learning by Analogy**:  
- https://psycnet.apa.org/doiLanding?doi=10.1037%2F0003-066X.52.1.32  
  
**The Analogical Mind**:  
- https://books.google.co.il/books?hl=iw&lr=&id=RfQX9wuf-2cC&oi=fnd&pg=PA23&dq=commonsense+analogy&ots=MvkNlPPSyo&sig=fsznpCd12ZuybvtaJnpqPzzvHk4&redir_esc=y#v=onepage&q=commonsense%20analogy&f=false   


## Additions
- https://examples.yourdictionary.com/analogy-ex.html  
- https://songmeanings.com
- https://www.songfacts.com