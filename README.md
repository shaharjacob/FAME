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
You should follow the following steps:  
1) <a href="https://www.docker.com/">Install docker</a>
2) Clone the repo using the following command:  
```bash
git clone https://github.com/shaharjacob/mapping-entities.git
```
3) Open your terminal in the root folder of the repo and type:  
```bash
docker-compose -f docker-compose.yml up -d
```  
**You can skip step 4 if you want to execuate using a yaml file**  
4) You should wait around 30-40 second, then open you browser at http://localhost:3000/  

If you want to see backend log (there are informative prints):  
```bash
docker-compose logs -f backend -t
```

If you want to see webapp log (nothing to do with it, just if you want to make sure that the app up successfully):  
```bash
docker-compose logs -f webapp -t
```

**Running without the demo**
After step 3, we will connect into the backend container using the following command:
```bash
docker exec -it backend bash
```
Now you ready to execute, please see below under **Execute**.  
&nbsp;  

### **Option 2:**
Install dependencies and run on your local PC.  
You should follow the following steps:  
1) Clone the repo using the following command:  
```bash
git clone https://github.com/shaharjacob/mapping-entities.git
```
2) Install dependencies using the following command: 
```bash
pip install -r requirements.txt
```  
**The following steps are for running the demo, if you dont want, skip to 'Execute' section**  
3) Install <a href="https://nodejs.org/en/">Node.js</a>, make sure its in your PATH.  
4) Now we need to install the react dependencies:  
```bash
cd webapp
npm install
```  
5) In `pakeage.json`, change the proxy from `http://backend:5031` to `http://localhost:5031`, the 'backend' is necessary when running the docker.
6) Now back to the root folder, and open the file ./backend/app/app.py, and **uncomment** the if main == ... section below.
7) from the root folder, run:
```bash
python backend/app/app.py
``` 
8) Now we just need to start the frontend:
```bash
cd webapp
npm start
```  
&nbsp;  

### **Option 3:**
Running on the university cluster using my folder (without demo, only backend).
1) ssh to phoenix cluster (depends on how you ssh but the server is phoenix.cs.huji.ac.il)
2) Go to my repo:  
```bash
cd /cs/labs/dshahaf/shahar.jacob/mapping-entities
```
3) Edit the shell script under the root folder called `runme.sh` with the command you want to run (see Execute section below).
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
By default, the script is running the all entries in the yaml. If you want to run specific entry, use `--specify {entry number, start from 1}`. You can specify muliple entries.  
For example, running the first entry only:  
```bash
python backend/evaluation/evaluation.py --yaml play_around.yaml --specify 1
```  
Running the first and the third entries:  
```bash
python backend/evaluation/evaluation.py --yaml play_around.yaml --specify 1 --specify 3
``` 

