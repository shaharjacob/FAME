# commonsense-analogy

## Goal
Our main goal is to understand analogy, for example:  

**1) Finding a good man is like finding a needle in a haystack:**  
**2) That's as useful as rearranging deck chairs on the Titanic:**  
**3) Earth rotate around the sun as electrons rotate around the nucleus**  
**4) Sunscreen protects against the sun just as a tarpaulin protects against rain**  
&nbsp;  
**More examples:**  
- https://examples.yourdictionary.com/analogy-ex.html 
- http://www.metamia.com  

&nbsp; 

# Table of content
- **graph.py**: Creating a graph which represent the nouns in the sentence.  
- **sentence_embadding.py**: Using sentence embadding to understand analogies.  
- **google_autocomplete.py**: Extracting information from google auto-complete.  
- **quasimodo.py**: Using quasimodo database for extracting information about connections between objects.  
- **wikifier.py**: Extracting information about the part-of-speech of the given text.  
&nbsp;  

## graph.py
1) Taking a text and extract the **nouns** using wikifier part-of-speech.  
2) For each noun, which will be a **node in our graph**, extract the information from quasimodo (single subject information).  
3) For each node, extract information from conceptNet.  
4) For each pair of nouns, extract inforamtion from google auto-complete, with a question ('why do', 'how do'). This will be on the edges.  
5) For each pair, extract information from quasimodo. This is also will be on the edges.  

```bash
python graph.py --text "electrons revolve around the nucleus as the earth revolve around the sun"

# the output graph can be found here:
# https://github.com/shaharjacob/commonsense-analogy/blob/main/graphs/earth_electrons_nucleus_sun.gv.pdf
```  
Or using it from other scripts:
```bash
from graph import run
from quasimodo import Quasimodo

text = "electrons revolve around the nucleus as the earth revolve around the sun"
quasimodo = Quasimodo(path="path-to-tsv")

run(text, quasimodo)
```

&nbsp;  

## sentence_embadding.py
The main purpose of this script is to give score for the sentences, such that we can decide if this is an analogy or not.  
But let start with simple use, just give similarity score for two sentences, base on SBERT model:  
```bash
from sentence_embadding import SentenceEmbedding

text1 = 'earth revolve around the sun'
text2 = 'earth circle the sun'
text3 = 'dog is the best friend of human'

model = SentenceEmbedding()
similarity = model.similarity(text1, text2, verbose=True)
similarity
-- 0.889

similarity = model.similarity(text1, text3, verbose=True)
similarity
-- 0.049

similarity = model.similarity(text1, text1, verbose=True)
similarity
-- 1.000
```  
Now, given two sentences, we examine all possible pairs, and select the pair of pairs with the highest score:  
```bash
python sentence_embadding.py --sentence1 "The nucleus, which is positively charged, and the electrons which are negatively charged, compose the atom" --sentence2 "On earth, the atmosphere protects us from the sun, but not enough so we use sunscreen"  --verbose --full_details --threshold 0.5
```
Or using it from other scripts:  
```bash
from sentence_embadding import run

sentence1 = "The nucleus, which is positively charged, and the electrons which are negatively charged, compose the atom"
sentence2 = "On earth, the atmosphere protects us from the sun, but not enough so we use sunscreen"
run(sentence1, sentence2, verbose=True, full_details=True, threshold=0.5)

# the output:
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/sentence_embedding_1.png?raw=true)  
&nbsp;  

**Notice** that in the first sentence it found 3 nouns: ['atom', 'electrons', 'nucleus'], in the second sentence it found also 3 nouns: ['atmosphere', 'earth', 'sun'], and from all possible options it found that the best match is: earth --> sun, electrons --> nucleus.  
&nbsp;  

Using --verbose will show you the scores for all the options:  
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/sentence_embedding_2.png?raw=true)  
&nbsp;  

Using --verbose --full-details will show you also inside the edges. The score is the average of the 5 best match (or less). Here is the top scores:  
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/sentence_embedding_3.png?raw=true)  
&nbsp;  

## google_autocomplete.py
This script using the API of google auto-complete the extract information.  
We are using question, subject and object which make the results more detailed.
By default the forms is: **{question} {subject} "*" {object}**  
for example: why do horses "*" stables  
&nbsp;  
by default, the script is looking also for the plural and singular forms of the inputs.  
For example, **horses** will convert into **horse** (in addition) and **stables** into **stable**.  
 
```bash
# using default example.yaml file without saving the results into a file
python google_autocomplete.py

# define a yaml file:
why do:
  - [horses, stables]

how do:
  - [horses, stables]


# You can use it outside the script by define a dictionary:
from google_autocomplete import process

d = {
  "why do": [
    ['horses', 'stables']
  ],
  "how do": [
    ['horses', 'stables']
  ]
}
suggestions = process(d)

# the output will be:
```  
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/google_engine_horses.png?raw=true)  
&nbsp;  

## quasimodo.py
This script using quasimodo database, which contains semantic information.  
We are intersting in the following fields: **subject**, **predicate**, **object**, and **plausibility**.  

```bash
# usage
from quasimodo import Quasimodo

quasimodo = Quasimodo(path='tsv/quasimodo.tsv')

# in case that the tsv not exists, you should run:
# import quasimodo
# quasimodo.merge_tsvs('quasimodo.tsv)

# get information on a single subject. n_largest will take the best matches according to quasimodo score.
quasimodo.get_subject_props('horse', n_largest=20, verbose=True, plural_and_singular=True)

# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_subject_object_props_quasimodo_api.png?raw=true)  

```bash
# get all the connections between each pair (connection is subject-object relationship)
quasimodo.get_subject_object_props('sun', 'earth', n_largest=20, verbose=True, plural_and_singular=True)

# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_subject_object_props_quasimodo_api.png?raw=true)  

```bash
# get all the similiar properties between two subjects
quasimodo.get_similarity_between_subjects('sun', 'earth', n_largest=20, verbose=True, plural_and_singular=True)

# so the output will be:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/get_similarity_between_subjects_quasimodo_api.png?raw=true)  
&nbsp;  

## wikifier.py
This script is extracting information from a text, such as part-of-speech.  
It using wikifier API for that purpose.  

**Notice**: The tool is ignoring special character inside the text, expect ','  
i.e. the output of "I lo!ve coding??" and "I love coding" will be the same.  

```bash
# usage
from wikifier import Wikifier

text_to_analyze = "I love coding but sometimes coding is very boring"
wikifier = Wikifier(text_to_analyze)
wikifier.get_part_of_speech()

# output:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/wikifier_get_part_of_speech2.png?raw=true)  

```bash
text_to_analyze = "sunscreen protects against the sun as a tarpaulin protects against rain"
wikifier = Wikifier(text_to_analyze)
wikifier.get_part_of_speech()

# output:  
```
![alt text](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/wikifier_get_part_of_speech1.png?raw=true)  
&nbsp;  
&nbsp;  

# References
- **Quasimodo**: https://quasimodo.r2.enst.fr/  
- **qa-srl**: http://qasrl.org/  
- **hayadata-lab**: http://www.hyadatalab.com/  
- **Wikifier**: http://wikifier.org/info.html/  
- **Sentence-Transformers**: https://sbert.net/
- **metamia**: http://www.metamia.com/  
&nbsp;  
  

# PDFs
- [Analogy-based Detection of Morphological and Semantic Relations With Word Embeddings: What Works and What Doesn’t](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/Analogy_based_Detection_of_Morphological_and_Semantic_Relations.pdf)  
- [Using Analogy To Acquire CommonsenseKnowledge from Human Contributors](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/Using_Analogy_To_Acquire_CommonsenseKnowledge_from_Human_Contributors.pdf)  
- [Reasoning and Learning by Analogy](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/UReasoning_and_Learning_by_Analogy.pdf)  
- [The Analogical Mind](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/The_Analogical_Mind.pdf)  
- [The Structure-Mapping Engine: Algorithm and Examples](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/structure_mapping_engine.pdf)  
- [The Latent Relation Mapping Engine: Algorithm and Experiments](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/The_Latent_Relation_Mapping_Engine.pdf)   

&nbsp;     

## Additions
- https://examples.yourdictionary.com/analogy-ex.html  
- https://songmeanings.com
- https://www.songfacts.com  
&nbsp;  


## Remote access via VScode
1) Follow the instructions here:  https://ca.huji.ac.il/book/samba-vpn-0  
&nbsp;&nbsp;- In the end you should have RA account + cisco VPN  
2) Connect to the VPN  
&nbsp;&nbsp;- host: samba.huji.ac.il  
&nbsp;&nbsp;- username: {ra-username}%ra (for example: shaharjacob%ra)  
&nbsp;&nbsp;- password: your password of the ra account (not the OTP!)  
3) Now you should install VScode from here: https://code.visualstudio.com/  
4) After the installation complete, open it, and in the left menu icons, choose **Extensions**.  
5) Search for **Remote: SSH** and install it (reload maybe required).  
6) Now, again in the left menu, search for **Remote Explorer**.  
7) Click on the + button (Add New).  
8) Now enter: `ssh -l <cse-username> river.cs.huji.ac.il`,&nbsp;&nbsp; for example: `ssh -l shahar.jacob river.cs.huji.ac.il`  
&nbsp;&nbsp;- **Notice**: ra-username and cse-username not necessarily have to be the same!  
9) click **linux** os if it ask, then it will ask your password, so enter your cse-password.  

&nbsp;  
You can now use the terminal for running python scripts.  
In addition, you can nevigate to the desire folder (and of course you can create/remove/edit files using the editor).


