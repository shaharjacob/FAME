# commonsense-analogy

## usage
```bash
# using default example.yaml file without saving the results into a file
python main.py

# using a config.yaml as a config file, and saving the results into out.csv
python main.py -f config.yaml -o out.csv
```

## quasimodo
```bash
# Download the .tsv file in necessary: 
https://nextcloud.mpi-klsb.mpg.de/index.php/s/Sioq6rKP8LmjMDQ/download?path=%2FLatest&files=quasimodo43.tsv

# usage
from quasimodo import Quasimodo
quasimodo = Quasimodo(path_to_tsv)
quasimodo.some_filter_method()...
```


## references
**Quasimodo**: https://quasimodo.r2.enst.fr/  
**qa-srl**: http://qasrl.org/  
**hayadata-lab**: http://www.hyadatalab.com/  
