# sentiment-anomaly

I started writing this after becoming unduly fascinated with the discussion on the WSB subreddit after the collapse of the GME bubble in late January 2021. The community gained 7m+ subscribers in the course of a couple of weeks. The comments are full of accusations of people being bots and shills either trying to inflate or depress sentiment about either about specific stocks or across the community as a whole. And there _is_ both incentive to do this and the appearance of it happening.

I decided the best way to stop myself reading the comments and trying to analyse the subtext was to write a bot to do it for me. That is this project. It's a reason to experiment with unsupervised sentiment analysis, with no labels or lexicon for incoming text. The aim is to detect sentiment anomalies over time from the flow of activity, in an attempt to differentiate what is "organic" from what is "engineered" - can it be done? This _doesn't_ store any user data, or make any attempt to look at individual history or do any conversational network analysis.

## Contents

 * `docker-compose.yml` for a Postgres database for the data collection
 * sqlalchemy schema for very minimal metadata about the posts and comments (upvotes and scores but no user data)
 * scripts to collect posts and comments with [PRAW](https://praw.readthedocs.io/en/latest/) (posts in a stream, and comments in batches, either on a cronjob or whenever you feel like looking at a fresh screenwall of swearing and emojis)
 * train different word embedding models, and a notebook for experimenting with them

```
 ('🙌', 1.0),
 ('🙌🏻', 0.6535108685493469),
 ('✋', 0.652143120765686),
 ('💎', 0.6348857879638672),
 ('🍆', 0.630488395690918)
```

## See also

 * [GLoVe model from Stanford CoreNLP](https://github.com/stanfordnlp/glove) - Used to generate some of the word vectors that are used with torchtext in the notebook
 * [sentometrics: An Integrated Framework for Textual Sentiment Time Series Aggregation and Prediction](https://github.com/SentometricsResearch/sentometrics) - a really interesting R package with a lot of the same aims and a lexicon approach which includes some investment sentiment data

## Caveats

If you want to train the [glove-python](https://github.com/maciejkula/glove-python) model in the notebook it is a pain as it _has_ to be python 3.6.5 - `glove-python`'s Cython no longer compiles on 3.7+ but latest jupyter throws 500 errors on 3.6.0. Miniconda3-4.5.4 provides 3.6.5 
