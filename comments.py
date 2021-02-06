"""Run sporadically and update db with recent comments.
Marks posts without new comments as defunct,
so we don't keep hitting the Reddit API for them.
"""
from datetime import datetime
from praw.models.reddit.comment import Comment as RedditComment
from praw.models.reddit.more import MoreComments
from sentiment_anomaly.collect import connect
from sentiment_anomaly.db import session, Submission, store_comment


if __name__ == '__main__':
    db = session()
    reddit = connect()
    now = datetime.now()

    posts = db.query(Submission).filter(Submission.defunct == False)
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

        # We're not seeing everything, with the defaults
        submission.comments.replace_more(128)
        comments = submission.comments.list()
        for comment in comments:
            if isinstance(comment, RedditComment):
                print(comment.body)
                store_comment(comment, db)
            if isinstance(comment, MoreComments):
                for more in comment.comments:
                    print(more.body)
                    store_comment(more, db)

        post.num_comments = submission.num_comments
        db.commit()
