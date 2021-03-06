"""Train a various word embedding models on reddit comments
"""
import re
from gensim.models import Word2Vec
from gensim.matutils import corpus2csc
from gensim.corpora import Dictionary
try:
    from glove import Glove, Corpus
except ModuleNotFoundError:
    pass
from nltk.corpus import stopwords
import numpy as np
from sentiment_anomaly.db import session, Comment, delete_autocomments

stopwords_list = stopwords.words('english')


def clean_data(w):
    w = w.lower()
    words = w.split()
    # don't filter all non-alphanumerics, so we keep emojis
    words = [re.sub(r'[\“\'\[\^\>\,\.\s\?\!\*\"]+$', '', w) for w in words]
    words = [re.sub(r'^[\“\'\[\^\>\,\.\s\?\!\*\"]+', '', w) for w in words]
    words = filter(lambda x: x not in stopwords_list, words)
    words = filter(lambda x: 'http' not in x, words)
    words = filter(lambda x: '[gif]' not in x, words)
    return list(words)


class CommentsWords():
    def __init__(self, db, score=0):
        # Trigger deletion of repetitive autocomments
        delete_autocomments(db)
        self.query = db.query(Comment).filter(score >= score)

    def __iter__(self):
        for message in self.query:
            text = message.body
            words = clean_data(text)
            yield words


def sentences(db):
    """List of all comments for tokenising, won't scale up well"""
    comments = db.query(Comment).all()
    return [clean_data(x.body) for x in comments]


def co_occurrence():
    """Create a sparse co-occurrence matrix of terms"""
    lines = sentences(session())
    dct = Dictionary(lines)
    bow_corpus = [dct.doc2bow(line) for line in lines]
    # This is the advice here: https://stackoverflow.com/a/49539666
    term_doc_mat = corpus2csc(bow_corpus)
    term_term_mat = np.dot(term_doc_mat, term_doc_mat.T)
    return dct, term_term_mat


def glove_corpus(score=0):
    corpus_model = Corpus()
    corpus_model.fit(CommentsWords(session(), score=score), window=10)
    return corpus_model


def train_word2vec(epochs=50, score=0):
    """Word2Vec for all comments
    Option for minimum comment score"""
    db = session()
    model = Word2Vec(min_count=3, window=3, size=300)

    model_input = CommentsWords(db, score=score)
    model.build_vocab(model_input)
    model.train(model_input, total_examples=model.corpus_count,
                epochs=50)  # Add callbacks, if required
    model.wv.save_word2vec_format('reddit_w2v_model.bin', binary=True)


def train_glove(epochs=50, threads=1, score=0):
    """Glove wants a co-occurrence matrix in certain form
    https://pypi.org/project/glove/
    Glove-python does more for you but requires python < 3.7
    """
    corpus_model = glove_corpus(score=score)
    glove = Glove(no_components=100, learning_rate=0.05)
    glove.fit(corpus_model.matrix, epochs=epochs,
              no_threads=threads, verbose=True)
    glove.add_dictionary(corpus_model.dictionary)

    glove.save('reddit.glove.model')
