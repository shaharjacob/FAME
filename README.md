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

## Table of content
- **graph.py**: Creating a graph which represent the nouns in the sentence.   
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

## google engine
This script using the API of google auto-complete the extract information.  
We are using question, subject and object which make the results more detailed.
By default the forms is: **{question} {subject} "*" {object}**  
for example: why do horses "*" stables  
&nbsp;  
by default, the script is looking also for the plural and singular forms of the inputs.  
For example, **horses** will convert into **horse** (in addition) and **stables** into **stable**.  
&nbsp;  
in addition, the script is able to looking for **synonyms**.  
It's taking the **best 5** results according to the word vector comparison.  
more information in dictionary.py section.  
Notice that this is a very heavy to load dictionary.py.  
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

## quasimodo
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

## Wikifier
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

## references
- **Quasimodo**: https://quasimodo.r2.enst.fr/  
- **qa-srl**: http://qasrl.org/  
- **hayadata-lab**: http://www.hyadatalab.com/  
- **Wikifier**: http://wikifier.org/info.html/  
- **gensim**: https://radimrehurek.com/gensim/  
&nbsp;  
  
## Analogy datasets
- **metamia**: http://www.metamia.com/
- **Vecto**: https://vecto.space/  
&nbsp;  

## PDFs
**Analogy-based Detection of Morphological and Semantic Relations With Word Embeddings: What Works and What Doesn’t**:  
- https://www.aclweb.org/anthology/N16-2002.pdf

**Using Analogy To Acquire CommonsenseKnowledge from Human Contributors**:  
- https://dspace.mit.edu/handle/1721.1/87342  
  
**Reasoning and Learning by Analogy**:  
- https://psycnet.apa.org/doiLanding?doi=10.1037%2F0003-066X.52.1.32  
  
**The Analogical Mind**:  
- https://books.google.co.il/books?hl=iw&lr=&id=RfQX9wuf-2cC&oi=fnd&pg=PA23&dq=commonsense+analogy&ots=MvkNlPPSyo&sig=fsznpCd12ZuybvtaJnpqPzzvHk4&redir_esc=y#v=onepage&q=commonsense%20analogy&f=false   
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


