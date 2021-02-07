"""Run sporadically and update db with recent comments.
Marks posts without new comments as defunct,
so we don't keep hitting the Reddit API for them.
"""
from datetime import datetime
import logging
from praw.models.reddit.comment import Comment as RedditComment
from praw.models.reddit.more import MoreComments
from sentiment_anomaly.collect import connect
from sentiment_anomaly.db import session, Submission, store_comment

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    db = session()
    reddit = connect()
    now = datetime.now()

    posts = db.query(Submission).filter(Submission.defunct == False) 
    logging.info(posts.count())
    for post in posts:
        submission = reddit.submission(post.id)

        if submission.num_comments == post.num_comments:
            age = (now - datetime.fromtimestamp(post.created_utc)).total_seconds()
            # posts with no new comments since 10 mins are now defunct
            if age > 600:
                print(f"defunct at {age}")
                post.defunct = True
                db.commit()
            continue

        # replace_more(None) -- no limit to comment traversal
        # but may hit the API too heavily?
        submission.comments.replace_more(None)
        comments = submission.comments.list()
        for comment in comments:
            if isinstance(comment, RedditComment):
                store_comment(comment, db, post=submission)
            if isinstance(comment, MoreComments):
                for more in comment.comments:
                    store_comment(more, db, post=submission)

        post.num_comments = submission.num_comments
        db.commit()
