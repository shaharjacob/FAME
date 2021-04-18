from sys import platform
from pathlib import Path

import nltk
from click import secho
from nltk.downloader import Downloader
default_download_folder = Path(Downloader().default_download_dir())
sub_folders = ['chunkers', 'grammars', 'misc', 'sentiment', 'taggers', 'corpora', 'help', 'models', 'stemmers', 'tokenizers']

def download_package(package: str, parent_dir: str):
    # https://stackoverflow.com/questions/23704510/how-do-i-test-whether-an-nltk-resource-is-already-installed-on-the-machine-runni
    try:
        nltk.data.find(f"{str(default_download_folder / parent_dir / package)}.zip")
    except:
        nltk.download(package, default_download_folder)