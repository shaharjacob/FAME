- **dictionary.py**: Extracting information on a word such as synonyms, antonyms, meanings and examples.  
- **metamia.py**: Building a database of analogies using http://www.metamia.com  
&nbsp;  

## Synonyms and Antonyms
The script is getting information on a specific word,s such as **synonyms**, **antonyms**, meanings and examples.  
The main use is for synonyms. There are two classes that getting synonyms, *WordNet* and *Dictionary*. And a third class called *Mixed*, which combained both together and taking the best results.
&nbsp;  

The best results are calculate with distance function based on word-vector, using gensim package (https://radimrehurek.com/gensim).  
Because of the use of this package, script that using this file (including google_autosuggest.py) have a long pre-loaing time (aroung 10-20 seconds).
&nbsp;

**notice**: words such as "Equus caballus" or "stalking-horse" that are not contains inside the gensim corups will be ignored.  

```bash
# usage
from dictionary import Mixed

# example 1 
mixed = Mixed('horse')
mixed.getSynonyms()

# output of WordNet: horse, cavalry, knight, buck, sawbuck
# output of Dictionary: horseback, racehorse, pony, chestnut, mare
# and the mixed output:
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/dictionary_best_5_for_horse.png?raw=true)  
&nbsp;   

```bash
# example 2 
mixed = Mixed('increase')
mixed.getSynonyms()

# output of WordNet: decrease, narrow, wane, depreciate
# output of Dictionary: increase, growth, gain, addition, increment
# and the mixed output:
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/dictionary_best_5_for_increase.png?raw=true)  
&nbsp;  

## metamia randomizer
This site (http://www.metamia.com) has a lot of complex analogy, but a list of all the analogy isn't available (or dataset), but there is a page which return a random analogy (http://www.metamia.com/randomly-sample-the-analogy-database).  
So the script is iterate this page and parsing the analogy, and by that creates a big dataset.  

```bash
# usage (-i is the number of iteration)
python metamia.py -i 100 -o out.csv
```  
&nbsp;  