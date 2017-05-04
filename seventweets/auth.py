from flask import request, jsonify
from functools import wraps
from seventweets.config import Config


API_TOKEN_HEADER = 'X-Api-Token'


def auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.headers.get(API_TOKEN_HEADER) != Config.API_TOKEN:
            return jsonify({"message": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper
