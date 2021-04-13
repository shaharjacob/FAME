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

**5) Sunscreen protects against the sun just as a tarpaulin protects against rain**
  
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

# heigher score_threshold -> more accurate results, but less amount.
quasimodo = Quasimodo(score_threshold=0.8)

# if for some reason you need the values of the subjects, predicates or objects, as an ordered list
# notice that it will take time only on the first time, after that it will use the saved files
# quasimodo = Quasimodo(score_threshold=0.8, save_ordered=True)
```

```bash
# get all the connections between each pair (connection is subject-object relationship)
quasimodo.get_connections(["sharp", "needle", "knife"])
# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections.png?raw=true)  

```bash
# you can also allow it to be more flexiable with the name by adding soft=True
quasimodo.get_connections(["sharp", "needle", "knife"], soft=True)
# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_soft.png?raw=true)  

```bash
# get all the common features between few subjects
quasimodo.get_connections_between_subjects(["horse", "cow", "chicken"])
# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_1.png?raw=true)
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_2.png?raw=true)
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_3.png?raw=true)
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_4_.png?raw=true)  

```bash
# also here you can allow flexiable name by adding soft=True
quasimodo.get_connections_between_subjects(["horse", "cow", "chicken"], soft=True)
# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_soft_1.png?raw=true)
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_soft_2.png?raw=true)
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_soft_3.png?raw=true)
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_connections_between_subjects_soft_4.png?raw=true)  

## Wikifier
```bash
# using for extract inforamtion from text (like part-of-speech)

# usage
from wikifier import Wikifier

text_to_analyze = "I love coding but sometimes coding is very boring"
wikifier = Wikifier(text_to_analyze)
wikifier.get_part_of_speech()

# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/wikifier_get_part_of_speech.png?raw=true)  

**Notice**: The tool is ignoring special character inside the text, expect ','  
i.e. the output of "I lo!ve coding??" and "I love coding" will be the same.


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
- **Wikifier**: http://wikifier.org/info.html/  

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

