<div align="center">
<img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/mapping-entities-hayadata.png?raw=true" width="500px" alt="mapping-entities"/>
</div>

## :dart: Goal
The main goal is to map entities from base domain to the target domain.  
For example, given the following base domain: `earth, sun, gravity, newton, universe`, and the following target domain: `electrons, nucleus, electricity, faraday, cell`, we would like to map entities from the base to the target:
- earth &nbsp;<img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/right_arrow.png?raw=true" alt="-->" width="18px"/> &nbsp;electrons
- sun &nbsp;<img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/right_arrow.png?raw=true" alt="-->" width="18px"/> &nbsp;nucleus
- gravity &nbsp;<img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/right_arrow.png?raw=true" alt="-->" width="18px"/> &nbsp;electricity
- newton &nbsp;<img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/right_arrow.png?raw=true" alt="-->" width="18px"/> &nbsp;faraday
- universe &nbsp;<img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/right_arrow.png?raw=true" alt="-->" width="18px"/> &nbsp;cell  

**Moreover**, if some of the entities are missing, we would like to suggest entities for good mapping.  
For example, if we will remove the entity `faraday` from the target, our mapping will leave `newton` without a map. So we would like to suggest entities (and of course, hopefully `faraday` will be one of the suggestions).  
&nbsp; 

## :clapper: Demo
For using our demo:
```bash
python app.py
cd webapp
npm start
```
#### :green_circle: Mapping
Given base entities and target entities, and it will apply the mapping.  
`http://localhost:3000/mapping-demo`  

![mapping-demo](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/mapping-demo.png?raw=true)  
 
![mapping](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/mapping.png?raw=true)  
 - &nbsp;&nbsp;:memo: **Note**: Clicking on edge will lead you to the relation between the nodes of the edge (like in *Relations* section below).  
&nbsp;  
#### :brown_circle: Relations:
Given pair from base, and pair from the target, it will show the relations between them.  
For example: given pair from base: (earth, sun) and pair from target: (electrons, nucleus).  
`http://localhost:3000/single-mapping-demo`  

![single-mapping-demo](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/relations-demo.png?raw=true)  
 
![relations-gui](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/relations1.png?raw=true)  
![relations-score](https://github.com/shaharjacob/commonsense-analogy/blob/main/images/relations2.png?raw=true)  
 - &nbsp;&nbsp;:memo: **Note**: Clicking *Taken from* entry will lead you the the coresponding relation.  
&nbsp;  
#### :large_blue_circle: Suggestions
Same as mapping-demo above, but in case of missing entities, it will give suggestions.  
TODO: image here  
`http://localhost:3000/mapping-with-suggestions-demo`  
&nbsp; 

## :books: Table of content
- **mapping.py**: TODO
- **suggestions.py**: TODO
- **concept_net.py**: Extracting entities information from ConcecptNet API.  
- **sentence_embadding.py**: Using sentence embadding to compare between properties.
- **google_autosuggest.py**: Extracting entities information from google auto-suggest.  
- **quasimodo.py**: Extracting entities information from quasimodo database.  
- **graph.py**: Creating a graph which represent the nouns in the sentence.  
&nbsp;  

#### :large_blue_circle: concept_net.py
We are using [ConceptNet](https://conceptnet.io/) API for extracting information for entities.  

```bash
from concept_net import get_entities_relations, get_entity_props

relations = get_entities_relations("earth", "sun")
# so the output will be:
['revolving around the']

props = get_entity_props("earth", n_best=10)
# so the output will be:
['4.5 billion years old', 'a word', 'an oblate sphereoid', 'an oblate spheroid', 'finite', 'flat', 'one astronomical unit from the Sun', 'one of many planets', 'receive rain from clouds', 'revolving around the sun', 'round like a ball', 'spherical', 'spherical in shape', 'very beautiful', 'very heavy']
```  
&nbsp;  

#### :brown_circle: sentence_embadding.py
We are using [sentence-transformers](https://www.sbert.net/) for measure similarities between sentences. In our case, sentences are going to be relations and properties.  
By default, we are using this model: `msmarco-distilbert-base-v4`  
But more models available [here](https://huggingface.co/models?sort=downloads&search=sentence-transformers&p=0)  
```bash
from sentence_embadding import SentenceEmbedding

model = SentenceEmbedding()

similarity = model.similarity('earth revolve around the sun', 'earth circle the sun')
-- 0.889

similarity = model.similarity('earth revolve around the sun', 'dog is the best friend of human')
-- 0.049

similarity = model.similarity('earth revolve around the sun', 'earth revolve around the sun')
-- 1.000
```  
&nbsp;  

#### :yellow_circle: google_autosuggest.py
This script using the API of google autosuggest to extract entities information.  
When we looking for relations between two entities, the form is: `{question} {entity1} .* {entity2}`  
When we looking for suggestions for new entities, the form is: `{question} {entity} {prop} .*` and `{question} .* {prop} {entity}`  
When we looking for entity properties, the form is: `{entity} {which} .*` when `which` can be `is a` or `is a type of`    
 
```bash
from google_autosuggest import get_entity_suggestions, get_entity_props, get_entities_relations

relations = get_entities_relations("earth", "sun").get("props)
# so the output will be:
['revolve around', 'orbit', 'circle the', 'rotate around', 'move around the', 'spin around the', 'not fall into', 'move around']

props = get_entity_props("newton")
# so the output will be:
['derived unit', 'fundamental unit', 'derived unit why', 'unit for measuring', 'unit of', 'fundamental unit or derived unit', 'measure of']

suggestions = get_entity_suggestions("electricity", "discovered")
# so the output will be:
['edison', 'benjamin', 'faraday', 'they']
```  

#### :red_circle: quasimodo.py
This script using quasimodo database, which contains semantic information.  
We are intersting in the following fields: **subject**, **predicate**, **object**, and **plausibility**.  

```bash
from quasimodo import Quasimodo

quasimodo = Quasimodo(path='tsv/quasimodo.tsv')

# in case that the tsv not exists, you should run:
# import quasimodo
# quasimodo.merge_tsvs('quasimodo.tsv)

# get information on a single subject. n_largest will take the best matches according to quasimodo score.
quasimodo.get_entity_props('sun', n_largest=5)
# so the output will be:
[('has property', 'star'), ('be in', 'sky'), ('has temperature', 'hot'), ('has color', 'yellow'), ('go', 'shining')]

# extract the relations between two object (the order is important!)
quasimodo.get_entities_relations('sun', 'earth', n_largest=5)
# so the output will be:
['be to', 'rotate around', 'pull in', 'orbit', 'be closest star to']

# extract the similarity between two object
quasimodo.get_similarity_between_entities('horse', 'cow', n_largest=5)
[('can', 'sit'), ('eat', 'grass'), ('has body part', 'teeth'), ('lay', 'down'), ('eat', 'hay')]
```
&nbsp;  


#### :purple_circle: graph.py
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

## :clipboard: References
- **Quasimodo**: https://quasimodo.r2.enst.fr/  
- **qa-srl**: http://qasrl.org/  
- **hayadata-lab**: http://www.hyadatalab.com/  
- **Wikifier**: http://wikifier.org/info.html/  
- **Sentence-Transformers**: https://sbert.net/
- **metamia**: http://www.metamia.com/  
&nbsp;  
  

## :pushpin: PDFs
- [Analogy-based Detection of Morphological and Semantic Relations With Word Embeddings: What Works and What Doesn’t](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/Analogy_based_Detection_of_Morphological_and_Semantic_Relations.pdf)  
- [Using Analogy To Acquire CommonsenseKnowledge from Human Contributors](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/Using_Analogy_To_Acquire_CommonsenseKnowledge_from_Human_Contributors.pdf)  
- [Reasoning and Learning by Analogy](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/UReasoning_and_Learning_by_Analogy.pdf)  
- [The Analogical Mind](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/The_Analogical_Mind.pdf)  
- [The Structure-Mapping Engine: Algorithm and Examples](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/structure_mapping_engine.pdf)  
- [The Latent Relation Mapping Engine: Algorithm and Experiments](https://github.com/shaharjacob/commonsense-analogy/blob/main/pdf/The_Latent_Relation_Mapping_Engine.pdf)   
