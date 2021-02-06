from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CONN = 'postgresql+psycopg2://sent:sent@localhost/sent'
Base = declarative_base()


class Submission(Base):
    __tablename__ = "submission"
    id = Column(String, primary_key=True)
    selftext = Column(String)
    title = Column(String)
    created_utc = Column(Integer)
    num_comments = Column(Integer)
    flair = Column(String)
    defunct = Column(Boolean)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(String, primary_key=True)
    body = Column(String)
    edited = Column(String)
    created_utc = Column(Integer)
    score = Column(Integer)


def session(connection_string=CONN):
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def store_comment(comment, db):
    """Accepts a praw.models.Comment object
    And a session() as above"""
    seen = db.query(Comment).get(comment.id)
    if seen:
        return
    else:
        # We want to see the new output too
        print(comment.body)
    comment = Comment(id=comment.id,
                      body=comment.body,
                      score=comment.score,
                      edited=comment.edited,
                      created_utc=int(comment.created_utc))
    db.add(comment)


def store_submission(submission, db):
    """Accepts a praw.models.Submission object
    And a session() as above"""
    post = db.query(Submission).get(submission.id)
    if post:
        return

    flair = None
    if hasattr(submission, 'link_flair_template_id'):
        flair = submission.link_flair_template_id
    sub = Submission(id=submission.id,
                     title=submission.title,
                     selftext=submission.selftext,
                     num_comments=submission.num_comments,
                     flair=flair,
                     created_utc=int(submission.created_utc))
    db.add(sub)
