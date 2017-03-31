"""
Module contains Flask application and routes 
"""
from flask import Flask, jsonify
from storage import Storage

app = Flask(__name__)


@app.route("/tweets", methods=['GET'])
def get_tweets():
    return jsonify(Storage.get_tweets())


@app.route("/tweets/<int:tweet_id>", methods=['GET'])
def get_tweet(tweet_id):
    tweet = Storage.get_tweet(tweet_id)
    return jsonify(tweet) if tweet else "Not found", 404
