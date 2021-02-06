"""Runs continuously and collects new reddit posts"""
import os
from sentiment_anomaly.collect import connect
from sentiment_anomaly.db import session, store_submission


if __name__ == '__main__':
    db = session()
    reddit = connect()
    subreddit = reddit.subreddit(os.environ.get('SUBREDDIT', "wallstreetbets"))

    for submission in subreddit.stream.submissions():
        print(submission.selftext)
        store_submission(submission, db)
        db.commit()
