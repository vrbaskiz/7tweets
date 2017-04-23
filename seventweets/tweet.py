"""
Module that defines Tweet model
"""


class Tweet(object):

    def __init__(self, id=None, name=None, tweet=None):
        self.id = id
        self.name = name
        self.tweet = tweet

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tweet': self.tweet
        }

    @classmethod
    def from_dict(cls, data):
        return Tweet(**data)