import json
import uuid

from datetime import datetime, timedelta, UTC

from src.backend_services.common.redis.redis import get_redis_conn


def create_session(user_uuid, user_data):
    '''
    
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


def update_session(session_uuid, user_uuid, user_data):
    '''
    
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


def delete_session(session_uuid, user_uuid):
    '''
    
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


def user_to_json(user):
    '''
    
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
