import json
from pathlib import Path

from tqdm import tqdm
import gensim.downloader as api
from sklearn.feature_extraction.text import CountVectorizer


def ngram(ngram_range: tuple = (1, 4)):   
    dataset = api.load("wiki-english-20171001")
    start_iteration = 1420
    docs_in_json = 100
    iterations = 5000
    for j in tqdm(range(start_iteration, iterations+1)):
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


def merge(dir_to_merge: str):
    merged_dict = {}
    for path in tqdm(Path(f"jsons/{dir_to_merge}").iterdir()):
        with open(path, 'r') as f:
            current_dict = json.load(f)
        merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
    with open(f"jsons/merged/{dir_to_merge}.json", 'w') as fw:
        json.dump(merged_dict, fw, indent="\t")


def frequency(strings):
    # merged_dict = {}
    # for path in tqdm(Path(f"jsons/merged/filtered").iterdir()):
    #     with open(path, 'r') as f:
    #         current_dict = json.load(f)
    #     merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
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

if __name__ == '__main__':
    # ngram()
    # frequency(["revolve around", "revolve around the", "orbit", "fall into", "have", "need", "floating on the water", "discover", "discovered"])
    
    for i in tqdm(range(280, 435, 5)):
        merge(f"{i}k-{i+5}k")
    
    # for i in tqdm(range(270, 435, 5)):
    #     filter_json(Path(f"jsons/merged/{i}k-{i+5}k.json"), 1)
    
    # merged_dict = {}
    # for path in tqdm(Path(f"jsons/merged/filtered").iterdir()):
    #     with open(path, 'r') as f:
    #         current_dict = json.load(f)
    #     merged_dict = {k: merged_dict.get(k, 0) + current_dict.get(k, 0) for k in set(merged_dict) | set(current_dict)}
    # with open(f"jsons/merged/filtered/all.json", 'w') as fw:
    #     json.dump(merged_dict, fw, indent="\t")
    
    
    # for thresh in [3,4,5,6]:
    #     path = Path(f"jsons/merged/filtered/all.json")
    #     with open(path, 'r') as f:
    #         current_dict = json.load(f)
    #     new_dict = {k: v for k, v in current_dict.items() if v > thresh}
    #     with open(path.parent.resolve() / f"{path.stem}_filter_{thresh}.json", 'w') as fw:
    #         json.dump(new_dict, fw, indent="\t")
    


    # root_dir = Path('C:\\Users\\User\\anaconda3\\Lib\\site-packages\\gensim')
    # all_dirs = []
    # for path in root_dir.iterdir():
    #     if not path.is_dir():
    #         continue
    #     size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
    #     # print(f"{path.name}: {size / 1_000_000_000}")
    #     all_dirs.append((path.name, size / 1_000_000_000))
    # all_dirs = sorted(all_dirs, key=lambda x: x[1], reverse=True)
    # for dir in all_dirs:
    #     print(dir)