from seventweets.config import Config
import pg8000


def init():
    db = pg8000.connect(**Config.DB_CONFIG)
    c = db.cursor()
    c.execute('DROP TABLE IF EXISTS tweets;')
    c.execute('''
        CREATE TABLE tweets (
        id SERIAL PRIMARY KEY,
        name VARCHAR(20) NOT NULL,
        tweet TEXT);
        ''')

    db.commit()
    c.close()
    db.close()
