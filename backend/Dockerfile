FROM python:3.8-buster

COPY . backend/
WORKDIR /backend

RUN pip install --upgrade pip
RUN pip install tqdm --no-cache-dir
RUN pip install click --no-cache-dir
RUN pip install flask --no-cache-dir
RUN pip install pyyaml --no-cache-dir
RUN pip install pandas --no-cache-dir
RUN pip install gensim --no-cache-dir
RUN pip install sklearn --no-cache-dir
RUN pip install inflect --no-cache-dir
RUN pip install requests --no-cache-dir
RUN pip install graphviz --no-cache-dir
RUN pip install networkx --no-cache-dir
RUN pip install beautifulsoup4 --no-cache-dir
RUN pip install transformers==4.10.3 --no-cache-dir
RUN pip install sentence_transformers --no-cache-dir
