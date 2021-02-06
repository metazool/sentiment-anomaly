"""Train a word2vec model on reddit comments
"""
from nltk.corpus import stopwords
from gensim.models import Word2Vec
import re
from sentiment_anomaly.db import session, Comment

stopwords_list = stopwords.words('english')


def clean_data(w):
    w = w.lower()
    words = w.split()
    # don't filter all non-alphanumerics, so we keep emojis
    words = [re.sub(r'[\,\.\s\?\!\*\"]+$', '', w) for w in words]
    words = [re.sub(r'^[\,\.\s\?\!\*\"]+', '', w) for w in words]
    words = filter(lambda x: x not in stopwords_list, words)
    words = filter(lambda x: 'http' not in x, words)
    return list(words)


class Comments():
    def __init__(self, db):
        self.query = db.query(Comment)

    def __iter__(self):
        for message in self.query:
            text = message.body
            words = clean_data(text)
            yield words


def train_word2vec():
    db = session()
    model = Word2Vec(min_count=3, window=3, size=300)

    model_input = Comments(db)
    model.build_vocab(model_input)
    model.train(model_input, total_examples=model.corpus_count,
                epochs=50)  # Add callbacks, if required
    model.wv.save_word2vec_format('reddit_w2v_model.bin', binary=True)
