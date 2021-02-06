from sentiment_anomaly.db import session, Submission

def test_db():
    db = session()
    sub = Submission(id='test',
                     title='test',
                     selftext='test')
    db.add(sub)
    db.commit()
