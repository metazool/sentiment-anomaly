import praw


def connect():
    """Configuration for `bot` should be in `praw.ini`"""
    reddit = praw.Reddit("bot")
    return reddit
