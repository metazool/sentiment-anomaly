from sentiment_anomaly.db import session, Submission, Comment


def test_db_sub():
    db = session()
    e = db.query(Submission).filter_by(id='test')
    e.delete()
    db.commit()

    sub = Submission(id='test',
                     title='test',
                     selftext='test')
    db.add(sub)
    db.commit()


def test_db_comment():
    db = session()
    e = db.query(Comment).filter_by(id='flah')
    e.delete()
    e = db.query(Submission).filter_by(id='test2')
    e.delete()
    db.commit()

    sub = Submission(id='test2',
                     title='test2',
                     selftext='test2')

    comm = Comment(id='flah',
                   body='flah',
                   post_id=sub.id)

    db.add(sub)
    db.add(comm)
    db.commit()
