FROM python:3.8-buster

COPY . backend/
WORKDIR /backend

##################################################
# for mac M1 #
# Update default packages
RUN apt-get update

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl

# Update new packages
RUN apt-get update

# Get Rust
# RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"
RUN . /root/.cargo/env
##################################################

RUN pip install --upgrade pip
RUN pip install tqdm --no-cache-dir
RUN pip install click --no-cache-dir
RUN pip install flask --no-cache-dir
RUN pip install openai --no-cache-dir
RUN pip install pyyaml --no-cache-dir
RUN pip install pandas --no-cache-dir
RUN pip install gensim --no-cache-dir
RUN pip install inflect --no-cache-dir
RUN pip install requests --no-cache-dir
RUN pip install graphviz --no-cache-dir
RUN pip install networkx --no-cache-dir
RUN pip install flask-cors --no-cache-dir
RUN pip install scikit-learn --no-cache-dir
RUN pip install python-dotenv --no-cache-dir
RUN pip install beautifulsoup4 --no-cache-dir
RUN pip install transformers==4.16 --no-cache-dir
RUN pip install sentence_transformers --no-cache-dir
