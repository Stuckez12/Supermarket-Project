'''
This file holds the method to get a connection to the redis server.
'''

import os
import redis

from redis import Redis
from redis.exceptions import ConnectionError, AuthenticationError
from typing import Tuple, Union


REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_DB = os.environ.get('REDIS_DB')

REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


def get_redis_conn() -> Tuple[bool, str, Union[Redis, None]]:
    '''
    This gets the connection to the redis server and returns
    the object used to communicate to the server.

    returns (bool, str, [Redis, None]): success flag, message and a redis object to the redis server
    '''

    status = False
    message = 'Connected Successfully'
    redis_client = None

    try:
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()

        status = True

    except (ValueError, TypeError):
        message = 'Invalid URL Provided'

    except ConnectionError:
        message = 'Unable To Connect To Redis Server'

    except AuthenticationError:
        message = 'Invalid Redis Authentication'

    except Exception:
        message = 'Unknown Error When Connecting To Redis Occurred'

    return status, message, redis_client
