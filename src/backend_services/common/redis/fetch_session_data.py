'''
This file handles the creation and management
of redis sessions that the frontend clients.
'''

import json

from typing import Tuple, Union

from src.backend_services.common.redis.redis import get_redis_conn


def get_session_user_data(session_uuid: str, user_uuid: str) -> Tuple[bool, str, Union[dict, None]]:
    '''
    Fetches the user data stored on a 

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
