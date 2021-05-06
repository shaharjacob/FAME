import tempfile
from pathlib import Path
from typing import Iterable, Dict, List, Tuple

import torch
from click import secho

from allennlp.models import Model
from allennlp.predictors import Predictor
from allennlp.common.util import JsonDict
from allennlp.data.instance import Instance
from allennlp.training.util import evaluate
from allennlp.data.tokenizers import Tokenizer
from allennlp.data import Vocabulary, DataLoader
from allennlp.nn.util import get_text_field_mask
from allennlp.data.tokenizers import SpacyTokenizer
from allennlp.training.optimizers import AdamOptimizer
from allennlp.data.data_loaders import SimpleDataLoader
from allennlp.training.metrics import CategoricalAccuracy
from allennlp.data.fields.text_field import TextFieldTensors
from allennlp.modules.seq2vec_encoders import Seq2VecEncoder
from allennlp.data.token_indexers import SingleIdTokenIndexer
from allennlp.data.fields import Field, TextField, LabelField
from allennlp.modules.token_embedders.embedding import Embedding
from allennlp.modules.text_field_embedders import TextFieldEmbedder
from allennlp.data.token_indexers.token_indexer import TokenIndexer
from allennlp.modules.seq2vec_encoders import BagOfEmbeddingsEncoder
from allennlp.training.trainer import GradientDescentTrainer, Trainer
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from allennlp.modules.text_field_embedders.basic_text_field_embedder import BasicTextFieldEmbedder


@Model.register('simple_classifier')
class SimpleClassifier(Model):
    def __init__(self,
                vocab: Vocabulary,
                embedder: TextFieldEmbedder,
                encoder: Seq2VecEncoder):
        super().__init__(vocab)
        self.embedder = embedder
        self.encoder = encoder
        num_labels = vocab.get_vocab_size("labels")
        self.classifier = torch.nn.Linear(encoder.get_output_dim(), num_labels)
        self.accuracy = CategoricalAccuracy()
    
    def forward(self,
                text: TextFieldTensors,
                label: torch.Tensor = None) -> Dict[str, torch.Tensor]:

        embedded_text = self.embedder(text) # Shape: (batch_size, num_tokens, embedding_dim)
        mask = get_text_field_mask(text) # Shape: (batch_size, num_tokens)
        encoded_text = self.encoder(embedded_text, mask) # Shape: (batch_size, encoding_dim)
        logits = self.classifier(encoded_text) # Shape: (batch_size, num_labels)
        probs = torch.nn.functional.softmax(logits, dim=1) # Shape: (batch_size, num_labels)
        output = {'probs': probs}
        if label is not None:
            self.accuracy(logits, label)
            output['loss'] = torch.nn.functional.cross_entropy(logits, label) # Shape: (1,)
        return output
    
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        return {"accuracy": self.accuracy.get_metric(reset)}


@DatasetReader.register('classification-tsv')
class ClassificationTsvReader(DatasetReader):
    def __init__(self,
                tokenizer: Tokenizer = None,
                token_indexers: Dict[str, TokenIndexer] = None,
                max_tokens: int = None,
                **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = tokenizer or WhitespaceTokenizer()
        self.token_indexers = token_indexers or {"tokens": SingleIdTokenIndexer()}
        self.max_tokens = max_tokens

    def text_to_instance(self, text: str, label: str = None) -> Instance:
        tokens = self.tokenizer.tokenize(text)
        if self.max_tokens:
            tokens = tokens[:self.max_tokens]
        text_field = TextField(tokens, self.token_indexers)
        fields = {'text': text_field}
        if label:
            fields['label'] = LabelField(label)
        return Instance(fields)

    def _read(self, file_path: str) -> Iterable[Instance]:
        with open(file_path, "r") as lines:
            for line in lines:
                text, sentiment = line.strip().split("\t")
                yield self.text_to_instance(text, sentiment)


@Predictor.register("sentence_classifier")
class SentenceClassifierPredictor(Predictor):
    def predict(self, sentence: str) -> JsonDict:
        # This method is implemented in the base class.
        return self.predict_json({"sentence": sentence})

    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        sentence = json_dict["sentence"]
        return self._dataset_reader.text_to_instance(sentence)
        

def read_data(reader: DatasetReader) -> Tuple[List[Instance], List[Instance]]:
    secho(f"[INFO] Reading data from 'movie_review/train.tsv' and 'movie_review/dev.tsv'", fg="blue")
    training_data = list(reader.read("movie_review/train.tsv"))
    validation_data = list(reader.read("movie_review/dev.tsv"))
    return training_data, validation_data


def build_vocab(instances: Iterable[Instance]) -> Vocabulary:
    secho(f"[INFO] Building the vocabulary", fg="blue")
    return Vocabulary.from_instances(instances)


def build_model(vocab: Vocabulary) -> Model:
    secho(f"[INFO] Building the model", fg="blue")
    vocab_size = vocab.get_vocab_size("tokens")
    embedder = BasicTextFieldEmbedder(
        {"tokens": Embedding(embedding_dim=10, num_embeddings=vocab_size)}
    )
    encoder = BagOfEmbeddingsEncoder(embedding_dim=10)
    return SimpleClassifier(vocab, embedder, encoder)


def build_data_loaders(train_data: List[Instance], dev_data: List[Instance]) -> Tuple[DataLoader, DataLoader]:
    train_loader = SimpleDataLoader(train_data, 8, shuffle=True)
    dev_loader = SimpleDataLoader(dev_data, 8, shuffle=False)
    return train_loader, dev_loader


def build_trainer(model: Model, serialization_dir: str, train_loader: DataLoader, dev_loader: DataLoader) -> Trainer:
    parameters = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    optimizer = AdamOptimizer(parameters)  # type: ignore
    trainer = GradientDescentTrainer(
        model=model,
        serialization_dir=serialization_dir,
        data_loader=train_loader,
        validation_data_loader=dev_loader,
        num_epochs=5,
        optimizer=optimizer,
    )
    return trainer


def run_training_loop():
    dataset_reader = ClassificationTsvReader()
    train_data, dev_data = read_data(dataset_reader)

    vocab = build_vocab(train_data + dev_data)
    model = build_model(vocab)

    train_loader, dev_loader = build_data_loaders(train_data, dev_data)
    train_loader.index_with(vocab)
    dev_loader.index_with(vocab)

    with tempfile.TemporaryDirectory() as serialization_dir:
        trainer = build_trainer(model, serialization_dir, train_loader, dev_loader)
        secho(f"[INFO] Start training", fg="blue")
        trainer.train()
        secho(f"[INFO] Finished training", fg="blue")

    return model, dataset_reader


def run_test(model: SimpleClassifier, dataset_reader: ClassificationTsvReader):
    test_data = list(dataset_reader.read("movie_review/test.tsv"))
    data_loader = SimpleDataLoader(test_data, batch_size=8)
    data_loader.index_with(model.vocab)
    return evaluate(model, data_loader)
    

if __name__ == "__main__":
    # model, dataset_reader = run_training_loop()
    # results = run_test(model, dataset_reader)
    # print(results)


    model, dataset_reader = run_training_loop()
    vocab = model.vocab
    predictor = SentenceClassifierPredictor(model, dataset_reader)

    output = predictor.predict("A good movie!")
    print(
        [
            (vocab.get_token_from_index(label_id, "labels"), prob)
            for label_id, prob in enumerate(output["probs"])
        ]
    )
    output = predictor.predict("This was a monstrous waste of time.")
    print(
        [
            (vocab.get_token_from_index(label_id, "labels"), prob)
            for label_id, prob in enumerate(output["probs"])
        ]
    )



