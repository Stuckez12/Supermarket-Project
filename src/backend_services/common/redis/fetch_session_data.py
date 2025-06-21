'''
This file handles the fetching and modification
of session data stored within redis.
'''

import json

from typing import Tuple, Union

from src.backend_services.common.redis.redis import get_redis_conn


def get_session_user_data(session_uuid: str, user_uuid: str) -> Tuple[bool, str, Union[dict, None]]:
    '''
    Fetches the user data stored withion an active session.

    user_uuid (str): the users uuid
    user_data (User): an sqlalchemy object containing one row for the specified users data

    return (str, int): the session uuid and the expiry time
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, message, None

    session_id = f'sid:{session_uuid}:{user_uuid}'
    redis_user_data = redis_client.get(session_id + ':user_data')

    if redis_user_data is None:
        return False, 'Unable To Fetch User Session Data', None

    user_data = json.loads(redis_user_data.decode('utf-8'))

    return True, '', user_data


def update_user_email_session(session_uuid: str, user_uuid: str, new_email: str, verified: bool=True) -> Tuple[bool, str]:
    '''
    Updates the email storeed on the redis session
    ensuring data is kept up to date, even when temporary.

    session_uuid (str): the clients session uuid identifier
    user_uuid (str): the users uuid
    verified (bool): specify whether to set the account as verified or unverified in redis [default - True]

    return (bool, str): success flag and message
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, message

    session_id = f'sid:{session_uuid}:{user_uuid}'

    expiry_time = redis_client.ttl(session_id + ':verified')
    redis_user_data = redis_client.get(session_id + ':user_data')

    user_data = json.loads(redis_user_data.decode('utf-8'))
    user_data['email'] = new_email

    if expiry_time != -1:
        redis_client.set(session_id + ':verified', json.dumps(verified), ex=expiry_time)
        redis_client.set(session_id + ':user_data', json.dumps(user_data), ex=expiry_time)

    else:
        redis_client.set(session_id + ':verified', json.dumps(verified))
        redis_client.set(session_id + ':user_data', json.dumps(user_data))

    print('New User_Data In Redis:', user_data)

    return True, ''
