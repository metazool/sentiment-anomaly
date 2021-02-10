import argparse
from sentiment_anomaly.vectors import train_word2vec

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs',
                        default=10,
                        help="Epochs to train, default 10")
    parser.add_argument('--score',
                        default=0,
                        help="Minimum comment score, default 0")
    args = parser.parse_args()

    train_word2vec(score=args.score)
