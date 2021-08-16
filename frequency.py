import json
from pathlib import Path

from tqdm import tqdm
import gensim.downloader as api
from sklearn.feature_extraction.text import CountVectorizer

import utils

class Frequencies():
    def __init__(self, path: str):
        self.data = utils.read_json(path)
    
    def apply_threshold(self, threshold):
        target_value = int((1-threshold) * len(self.data))
        self.data = {k: v for i, (k, v) in enumerate(self.data.items()) if i > target_value}
    
    def get(self, sequence: str):
        print(f"{sequence}: {self.data.get(sequence, 0)}")
        print()
        return self.data.get(sequence, 0)

    def exists(self, sequence: str):
        return sequence in self.data

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
        with open(f"jsons/{(j-1)*docs_in_json}-{j*docs_in_json}.json", 'w') as f:
            json.dump(words_freq, f, indent="\t")


def group_jsons(start: int, end: int):
    for i in range(start, end, 5000):
        jsons = Path("jsons")
        root_dir = jsons / f"{int(i/1000)}k-{int(i/1000)+5}k"
        root_dir.mkdir()
        for j in range(i, i+5000, 100):
            (jsons / f"{j}-{j+100}.json").replace(root_dir / f"{j}-{j+100}.json")


def merge(dir_to_merge: str):
    merged_dict = {}
    for path in tqdm(Path(f"jsons/{dir_to_merge}").iterdir()):
        with open(path, 'r') as f:
            current_dict = json.load(f)
        merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
    with open(f"jsons/merged/{dir_to_merge}.json", 'w') as fw:
        json.dump(merged_dict, fw, indent="\t")


def merge_all_filtered():
    merged_dict = {}
    for path in tqdm(Path(f"jsons/merged/filtered").iterdir()):
        with open(path, 'r') as f:
            current_dict = json.load(f)
        merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
    with open(f"jsons/merged/filtered/all_1m.json", 'w') as fw:
        json.dump(merged_dict, fw, indent="\t")


def frequency(strings):
    with open(f"jsons/merged/filtered/all.json", 'r') as f:
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
        path = Path(f"jsons/merged/filtered/all_1m.json")
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


if __name__ == '__main__':
    freq = Frequencies('jsons/merged/20%/all_1m_filter_2_sort.json')
    # freq.write_order_json('jsons/merged/20%/all_1m_filter_2_sort.json')
    freq.apply_threshold(0.9999)
    freq.get("revolve around")
    freq.get("revolve around the")
    freq.get("orbit")
    freq.get("fall into")
    freq.get("have")
    freq.get("need")
    freq.get("floating on the water")
    freq.get("discover")
    freq.get("discovered")
    freq.get("related to")
    freq.get("bigger than")
    
    
    
    
    
    
    
    
    # ngram()
    # filter_merged_json()
    # for i in tqdm(range(990, 1000, 5)):
    #     merge(f"{i}k-{i+5}k")
    
    # for i in tqdm(range(990, 1000, 5)):
    #     filter_json(Path(f"jsons/merged/{i}k-{i+5}k.json"), 1)
    
    
    

    
    