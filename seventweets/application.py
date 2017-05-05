"""
Module contains Flask application and routes.
"""
from flask import Flask, jsonify
from seventweets.storage import Storage
from seventweets.tweet import Tweet
from seventweets.auth import auth
from flask import request

app = Flask(__name__)


@app.route("/tweets", methods=['GET'])
def get_tweets():
    return jsonify([tweet.to_dict() for tweet in Storage.get_tweets()])


@app.route("/tweets/<int:tweet_id>", methods=['GET'])
def get_tweet(tweet_id):
    tweet = Storage.get_tweet(tweet_id)
    return jsonify(tweet.to_dict()) if tweet else ("Not found", 404)


@app.route("/tweets", methods=['POST'])
def add_tweet():
    tweet = Tweet.from_dict(request.json)
    tweet = Storage.add_tweet(tweet)
    return jsonify(tweet.to_dict())


@app.route("/tweets/<int:tweet_id>", methods=['DELETE'])
@auth
def delete_tweet(tweet_id):
    Storage.delete_tweet(tweet_id)
    return '', 204
