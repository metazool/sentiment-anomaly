from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, relationship

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
    post_id = Column(String, ForeignKey(Submission.id))  # , primary_key=True)
    post = relationship('Submission', foreign_keys=[post_id])


def engine(connection_string=CONN):
    drive = create_engine(connection_string)
    return drive


def session():
    drive = engine()
    Base.metadata.create_all(drive)
    Session = sessionmaker(bind=drive)
    session = Session()
    return session


def store_comment(comment, db, post=None):
    """Accepts a praw.models.Comment object
    And a session() as above"""
    seen = db.query(Comment).get(comment.id)
    if seen:
        if comment.score > seen.score:
            seen.score = comment.score
        return
    else:
        # We want to see the new output too
        print(comment.body)
    post_id = None
    if post:
        post_id = post.id
    comment = Comment(id=comment.id,
                      body=comment.body,
                      score=comment.score,
                      edited=comment.edited,
                      created_utc=int(comment.created_utc),
                      post_id=post_id)
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
                     defunct=False,
                     created_utc=int(submission.created_utc))
    db.add(sub)


def delete_autocomments(db):
    """Delete comment records created by automated processes"""
    autocomments = [
            "%action was performed automatically%"
            ]
    for comment in autocomments:
        autos = db.query(Comment).filter(
                func.lower(Comment.body).like(comment))
        for post in autos:
            db.delete(post)
    db.commit()
