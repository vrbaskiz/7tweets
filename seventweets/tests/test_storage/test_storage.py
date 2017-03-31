from seventweets.storage import Storage


def test_get_tweets():
    tweets = Storage.get_tweets()
    assert isinstance(tweets, list)


def test_get_tweet():
    tweet = Storage.get_tweet(12)
    assert tweet is not None, "Tweet should not be None"
