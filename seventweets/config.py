import os
import binascii


def generate_api_token():
    """
    Generates random token.
    """
    return binascii.b2a_hex(os.urandom(15))


class Config(object):
    """
    Global object to hold configuration.
    """
    DB_CONFIG = dict(user=os.environ.get('ST_DB_USER', 'radionica'),
                     database=os.environ.get('ST_DB_NAME', 'radionica'),
                     host=os.environ.get('ST_DB_HOST', 'localhost'),
                     password=os.environ.get('ST_DB_PASS', None),
                     port=int(os.environ.get('ST_DB_PORT', 5432)))
    NAME = os.environ.get('ST_NAME', 'break')
    # TODO: If token is not provided, no one knows it - log it somewhere
    API_TOKEN = os.environ.get('ST_API_TOKEN', generate_api_token())
