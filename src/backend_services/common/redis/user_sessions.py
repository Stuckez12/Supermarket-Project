'''
This file handles the creation and management
of redis sessions that the frontend clients.
'''

import json
import uuid

from datetime import datetime, timedelta, UTC
from typing import Tuple

from src.backend_services.account.database.models import User
from src.backend_services.common.proto.user_login_pb2 import UserData
from src.backend_services.common.redis.redis import get_redis_conn


def create_session(user_uuid: str, user_data: User) -> Tuple[str, int]:
    '''
    Creates two session instances with an hour time limit.
    An instance each for the user data and whether the user has been verified.

    user_uuid (str): the users uuid
    user_data (User): an sqlalchemy object containing one row for the specified users data

    return (str, int): the session uuid and the expiry time
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, message

    session_uuid = str(uuid.uuid4())
    session_id = f'sid:{session_uuid}:{user_uuid}'

    redis_client.set(session_id + ':user_data', json.dumps(user_to_json(user_data)))
    redis_client.set(session_id + ':verified', json.dumps(user_data.is_verified()))

    redis_client.expire(session_id + ':user_data', 3600) # 1 hour expiry
    redis_client.expire(session_id + ':verified', 3600) # 1 hour expiry

    expiry_time = datetime.now(UTC) + timedelta(hours=1)
    unix_time = int(expiry_time.timestamp())

    print('Stored User Session Data:', redis_client.get(session_id + ':user_data'))
    print('Session UUID:', session_uuid)

    return session_uuid, unix_time


def update_session(session_uuid: str, user_uuid: str, user_data: User):
    '''
    Updates the two existing session instances with an hour time limit.
    An instance each for the user data and whether the user has been verified.

    session_uuid (str): the clients session uuid identifier
    user_uuid (str): the users uuid
    user_data (User): an sqlalchemy object containing one row for the specified users data

    return (str, int): the session uuid and the expiry time
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, message

    session_id = f'sid:{session_uuid}:{user_uuid}'

    redis_client.set(session_id + ':user_data', json.dumps(user_to_json(user_data)))
    redis_client.set(session_id + ':verified', json.dumps(user_data.is_verified()))

    redis_client.expire(session_id + ':user_data', 3600) # 1 hour expiry
    redis_client.expire(session_id + ':verified', 3600) # 1 hour expiry

    expiry_time = datetime.now(UTC) + timedelta(hours=1)
    unix_time = int(expiry_time.timestamp())

    print('Stored User Session Data:', redis_client.get(session_id + ':user_data'))
    print('Session UUID:', session_uuid)

    return session_uuid, unix_time


def delete_session(session_uuid: str, user_uuid: str) -> Tuple[bool, str]:
    '''
    Deletes the sessions linked to the user.

    session_uuid (str): the clients session uuid identifier
    user_uuid (str): the users uuid

    return (bool, str): the success flag and a message
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, message
    
    session_id = f'sid:{session_uuid}:{user_uuid}'
    
    u_data = redis_client.delete(session_id + ':user_data')
    ver = redis_client.delete(session_id + ':verified')

    success = bool(u_data and ver)

    if not success:
        return False, 'Unable To Log Out'

    return True, 'User Logged Out'


def user_to_json(user: UserData) -> dict:
    '''
    Converts the gRPC UserData Message into a dict.

    user (UserData): the response message from the gRPC server

    return (dict): a dict of the users public details
    '''

    return {
        'uuid': user.uuid,
        'email': user.email,
        'password_last_changed_at': user.password_last_changed_at,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'gender': user.gender,
        'date_of_birth': user.date_of_birth.isoformat(),
        'created_at': user.created_at,
        'updated_at': user.updated_at,
        'last_login': user.last_login,
        'email_verified': user.email_verified,
        'user_status': user.user_status,
        'user_role': user.user_role,
    }
