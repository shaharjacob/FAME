import json
from typing import Union
from pathlib import Path

from tqdm import tqdm
import gensim.downloader as api
from sklearn.feature_extraction.text import CountVectorizer

from utils import utils

root = Path(__file__).resolve().parent.parent.parent

class Frequencies():
    def __init__(self, path: Union[str, Path], threshold: float):
        self.data = utils.read_json(path)
        self.stopwords = {}
        self.apply_threshold(threshold)
        self.manual_stopwords()
    
    def apply_threshold(self, threshold):
        target_value = threshold if threshold >= 1 else int(threshold * len(self.data))
        self.stopwords = {k: v for i, (k, v) in enumerate(self.data.items()) if i < target_value}
    
    def manual_stopwords(self):
        with open(root / 'backend' / 'frequency' / 'stopwords.txt', 'r') as f:
            words = [word.strip() for word in f.read().split('\n')]
        for word in words:
            if word not in self.stopwords:
                self.stopwords[word] = self.data.get(word, 1)
    
    def get(self, sequence: str):
        if sequence in self.stopwords:
            return 0
        return self.data.get(sequence, 0)

    def write_order_json(self, output: str):
        self.data = {k: v for k, v in sorted(self.data.items(), key=lambda x: x[1], reverse=True)}
        with open(output, 'w') as fw:
            json.dump(self.data, fw, indent="\t")
    

def ngram(ngram_range: tuple = (1, 4)):   
    dataset = api.load("wiki-english-20171001")
    start_iteration = 5000
    docs_in_json = 100
    iterations = 5000
    for j in tqdm(range(start_iteration, start_iteration + iterations + 1)):
        all_text = []
        for i, doc in enumerate(dataset):
            if i <= (j-1)*docs_in_json:
                continue
            if i >= j*docs_in_json:
                break
            doc = list(map(lambda x: x.replace("\n", " ").replace("\'", "").replace("*", "").replace("'", ""), doc["section_texts"]))    
            all_text.append(" ".join(doc))

        vec = CountVectorizer(ngram_range=ngram_range, lowercase=True, binary=True).fit(all_text)
        bag_of_words = vec.transform(all_text)
        sum_words = bag_of_words.sum(axis=0)
        words_freq = {word: int(sum_words[0, idx]) for word, idx in vec.vocabulary_.items()}
        json_folder = root / 'backend' / 'frequency' / 'jsons'
        if not json_folder.exists():
            json_folder.mkdir()
        with open(root / 'backend' / 'frequency' / 'jsons' / f"{(j-1)*docs_in_json}-{j*docs_in_json}.json", 'w') as f:
            json.dump(words_freq, f, indent="\t")


def group_jsons(start: int, end: int):
    for i in range(start, end, 5000):
        jsons = root / 'backend' / 'frequency' / 'jsons'
        root_dir = jsons / f"{int(i/1000)}k-{int(i/1000)+5}k"
        root_dir.mkdir()
        for j in range(i, i+5000, 100):
            (jsons / f"{j}-{j+100}.json").replace(root_dir / f"{j}-{j+100}.json")


def merge(dir_to_merge: str):
    merged_dict = {}
    for path in tqdm(Path(root / 'backend' / 'frequency' / 'jsons' / f"{dir_to_merge}").iterdir()):
        with open(path, 'r') as f:
            current_dict = json.load(f)
        merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
        
    json_folder = root / 'backend' / 'frequency' / 'jsons'
    if not json_folder.exists():
        json_folder.mkdir()
        
    merged_folder = json_folder / 'merged'
    if not merged_folder.exists():
        merged_folder.mkdir()
        
    with open(merged_folder / f"{dir_to_merge}.json", 'w') as fw:
        json.dump(merged_dict, fw, indent="\t")


def merge_all_filtered():
    merged_dict = {}
    for path in tqdm(Path(root / 'backend' / 'frequency' / 'jsons' / 'merged' / 'filtered').iterdir()):
        with open(path, 'r') as f:
            current_dict = json.load(f)
        merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
    with open(root / 'backend' / 'frequency' / 'jsons' / 'merged' / 'filtered' / 'all_1m.json', 'w') as fw:
        json.dump(merged_dict, fw, indent="\t")


def frequency(strings):
    with open(root / 'backend' / 'frequency' / 'jsons' / 'merged' / 'filtered' / 'all.json', 'r') as f:
        merged_dict = json.load(f)
    for s in strings:
        print(f"{s}: {merged_dict.get(s, 0)}")


def filter_json(path: Path, thresh: int):
    with open(path, 'r') as f:
        current_dict = json.load(f)
    new_dict = {k: v for k, v in current_dict.items() if v > thresh}
    with open(path.parent.resolve() / "filtered" / f"{path.stem}_filter.json", 'w') as fw:
        json.dump(new_dict, fw, indent="\t")


def filter_merged_json():
    for thresh in [2, 3, 4, 5, 6]:
        path = Path(root / 'backend' / 'frequency' / 'jsons' / 'merged' / '20%' / 'all_1m.json')
        with open(path, 'r') as f:
            current_dict = json.load(f)
        new_dict = {k: v for k, v in current_dict.items() if v > thresh}
        with open(path.parent.resolve() / f"{path.stem}_filter_{thresh}.json", 'w') as fw:
            json.dump(new_dict, fw, indent="\t")


def check_space():
    # root_dir = Path('C:\\Users\\User\\anaconda3\\Lib\\site-packages\\gensim')
    # root_dir = Path('C:\\Users\\User\\AppData\\Local')
    root_dir = Path('C:\\Users\\User\\Desktop')
    all_dirs = []
    for path in root_dir.iterdir():
        if not path.is_dir():
            continue
        size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
        all_dirs.append((path.name, size / 1_000_000_000))
    all_dirs = sorted(all_dirs, key=lambda x: x[1], reverse=True)
    for dir in all_dirs:
        print(dir)


def create_json_for_ci():
    merged_dict = {}
    filtered = Path(root / 'jsons' / 'merged' / 'filtered')
    for path in tqdm(filtered.iterdir()):
        with open(path, 'r') as f:
            current_dict = json.load(f)
        merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
        
    new_dict = {k: v for k, v in sorted(merged_dict.items(), key=lambda x: x[1], reverse=True) if v > 3}
    parent_dir = filtered.parent.resolve()
    if not (parent_dir / '20%').is_dir:
        (filtered / '20%').mkdir()
    with open(parent_dir / '20%' / 'all_1m_filter_3_sort.json', 'w') as fw:
        json.dump(new_dict, fw, indent="\t")
    

if __name__ == '__main__':
    pass
    # create_json_for_ci()

    # freq = Frequencies('jsons/merged/20%/all_1m_filter_3.json', 0)
    # freq.write_order_json('jsons/merged/20%/all_1m_filter_3_sort.json')
    # freq.apply_threshold(0.00005)
    # freq.get("revolve around")
    # freq.get("revolve around the")
    # freq.get("orbit")
    # freq.get("fall into")
    # freq.get("have")
    # freq.get("need")
    # freq.get("floating on the water")
    # freq.get("discover")
    # freq.get("discovered")
    # freq.get("related to")
    # freq.get("bigger than")
    
    # ngram()
    # filter_merged_json()
    # for i in tqdm(range(990, 1000, 5)):
    #     merge(f"{i}k-{i+5}k")
    
    # for i in tqdm(range(990, 1000, 5)):
    #     filter_json(Path(f"jsons/merged/{i}k-{i+5}k.json"), 1)
    
    
    

    
    