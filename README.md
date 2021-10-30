<p align="center">
  <img src="https://github.com/shaharjacob/commonsense-analogy/blob/main/images/hyadata.png?raw=true" width="300px" alt="hyadata"/>
  
  <div align="center">Structure mapping automation based on sentence embadding</div>
</p>

<p align="center">
  <a href="https://github.com/shaharjacob/mapping-entities/actions"><img src="https://img.shields.io/badge/CI-passing-brightgreen?logo=github" alt="ci"/></a>
  <a href="https://new.huji.ac.il/"><img src="https://img.shields.io/badge/license-HUJI-blue" alt="license"/></a>
  <a href="https://hub.docker.com/"><img src="https://img.shields.io/badge/-docker-gray?logo=docker" alt="docker"/></a>
  <a href="https://reactjs.org/"><img src="https://img.shields.io/badge/-react-grey?logo=react" alt="react"/></a>
  <a href="http://www.hyadatalab.com/"><img src="https://img.shields.io/badge/-hyadata-orange" alt="hyadata"/></a>
</p>

## Useage  
### **Option 1:**
Using a docker.  
First, you should <a href="https://www.docker.com/">install docker</a>.  

Now, for **exploring with GUI webapp**, the steps are:  
```bash
# pulling the images  
docker pull shaharjacob/msbackend  
docker pull shaharjacob/mswebapp  

# crating a network to combine both containers  
docker network create "mapping-entities"  

# running both containers
docker run -d -p 5031:5031 --name backend --network "mapping-entities" -e "FLASK_ENV=development" -e "FLASK_APP=app.app" -e "SENTENCE_TRANSFORMERS_HOME=cache" shaharjacob/msbackend flask run --host "0.0.0.0" --port 5031  
docker run -d -p 3000:3000 --name webapp --network "mapping-entities" shaharjacob/mswebapp npm start
```

After few seconds you can open browser at: <a href="https://localhost:3000/">https://localhost:3000/</a>  
The first run may take a few second because it download the sBERT model into the container.  

**Verbose:**  
If you want to make sure that webapp container load successfully:
```bash
docker logs -f webapp
```  
If you want to see backend verbose, use:  
```bash
docker logs -f backend
```  
Exit from the verbose mode can be done with `ctrl + c`.  
&nbsp;  


If you want to **run without the demo**, you need to connect to the backend container.      
To do that you just need to type:  
```bash
docker exec -it backend bash
```  
You should be now in **backend** folder, and should run:  
```bash
python evaluation/evaluation.py --yaml play_around.yaml
```
More details about the execute command can be found under **Execute** section.  
&nbsp;  


### **Option 2:**
Install dependencies and run on your local PC.  
```bash
git clone https://github.com/shaharjacob/mapping-entities.git
cd mapping-entities
pip install -r requirements.txt
```  
Now you ready for the execute command detailed in **Execute** section.  
&nbsp;  

**FOR GUI ONLY**  
If you want the GUI, you should do the following steps (in addition to the steps above):  
1) Install <a href="https://nodejs.org/en/">Node.js</a>, make sure its in your PATH. Install version 16.13.0.  
2) Now we need to install the react dependencies:  
```bash
cd webapp
npm ci
```  
3) In `pakeage.json`, change the proxy from `http://backend:5031` to `http://localhost:5031`, the 'backend' is necessary when running the docker.
4) Now back to the root folder, and open the file ./backend/app/app.py, and **uncomment** the if main == ... section below.
5) from the root folder, run:
```bash
python backend/app/app.py
``` 
6) Now we just need to start the frontend:
```bash
cd webapp
npm start
```  
&nbsp;  


### **Option 3:**
Running on the university cluster using exsiting repo (without demo, only backend).
1) ssh to phoenix cluster.
2) ```cd /cs/labs/dshahaf/shahar.jacob/mapping-entities```
3) Edit the shell script under the root folder called `runme.sh` with the command you want to run (see **Execute** section).
4) Run the following command:  
```bash
sbatch --mem=6gm -c2 --time=12:0:0 --gres=gpu:2 --verbose "runme.sh"
```  
See the log with the command:  
```bash
tail -f slurm-{job-id}.out
```  
The job id shown when the job in submitted.  
&nbsp;  

## Execute
Execution is done by configure a yaml file.
Examples for yaml files can be found under: `backend/evalution`, in particular you can use `backend/evalution/play_around.yaml`.  
You can see inside this file a template (in comment), and another example.  
After editting the yaml by adding another entry, you can use the following command:  
```bash
python backend/evaluation/evaluation.py --yaml play_around.yaml
```  
If you want the suggestions to be available, add `--suggestions`.  This is not recommend unless you looking for suggstions.  
By default, the script is running all the entries in the yaml. If you want to run specific entry, use `--specify {entry number, start from 1}`. You can specify muliple entries.  
For example, running the first entry only:  
```bash
python backend/evaluation/evaluation.py --yaml play_around.yaml --specify 1
```  
Running the first and the third entries:  
```bash
python backend/evaluation/evaluation.py --yaml play_around.yaml --specify 1 --specify 3
``` 
