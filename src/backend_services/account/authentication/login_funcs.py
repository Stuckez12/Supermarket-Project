'''
Contains all the supporting functions that are used to
manage and control the users actions for authentication.
'''

import json
import os

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Tuple

from src.backend_services.account.database.models import User, UserLoginAttempts
from src.backend_services.common.email.email_client import email_client
from src.backend_services.common.proto import user_login_pb2
from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response
from src.backend_services.common.redis.redis import get_redis_conn


# environment variables
ATTEMPTS_BEFORE_LOCK = int(os.environ.get('ACCOUNT_MAX_LOGIN_ATTEMPTS'))


def send_and_store_otp_code(email: str, return_status: HTTP_Response, replace_message: bool=True):
    '''
    Sends the OTP email to the client and saves the OTP ID onto redis for 10 mins.

    email (str): the provided users email to validate
    return_status (HTTP_Response): the response to send back to the client
    replace_message (bool): whether to replace the error message with a generic message

    return (bool, HTTP_Response): success flag and http status response message
    '''

    success, http_status, message, otp_id = email_client.send_otp_email([email])

    if not success:
        return_status.success = success
        return_status.http_status = http_status

        if replace_message:
            return_status.message = 'Unable To Send Verification Email'

        else:
            return_status.message = message
            return_status.error.extend(['Unable To Send Verification Email'])

        return False, return_status

    success, message, redis_client = get_redis_conn()

    if not success:
        return_status.success = False
        return_status.http_status = 500

        if replace_message:
            return_status.message = 'Unable To Connect To Redis Service'

        else:
            return_status.error.extend(['Unable To Connect To Redis Service'])

        return_status.error.extend([message])

        return False, return_status

    redis_client.set(
        name=f'verification:otp:{email}',
        value=otp_id,
        ex=600  # 10 minutes
    )

    # Testing purposes only for print statement
    print('Fetched Code From Redis:', redis_client.get(f'verification:otp:{email}'))

    return True, None


def check_email_session_data(email: str, session_uuid: str, return_status: HTTP_Response) -> Tuple[bool, HTTP_Response]:
    '''
    Checks whether the email provided and the session email is equal.

    email (str): the provided users email to validate
    session_uuid (str): the frontend clients session
    return_status (HTTP_Response): the response to send back to the client

    return (bool, HTTP_Response): success flag and http status response message
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return_status.success = False
        return_status.http_status = 500
        return_status.message = message

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)

    data = redis_client.scan_iter(match=f'sid:{session_uuid}:*:user_data', count=1, _type='string')

    received_data = None
    passed = False

    if data is not None:
        received_data = list(data)
        passed = True

    if not passed or len(received_data) == 0:
        return_status.success = False
        return_status.http_status = 400
        return_status.message = 'Session Either Expired Or Never Existed'

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)

    user_data = redis_client.get(received_data[0])

    if user_data is None:
        return_status.success = False
        return_status.http_status = 400
        return_status.message = 'Session Has No User Data'

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)

    user_session_data = json.loads(user_data)

    print(user_session_data)

    if user_session_data['email'] != email:
        return_status.success = False
        return_status.http_status = 400
        return_status.message = 'Logged In Account Mismatch With Provided Email'

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)

    return True, None


def iter_failed_attempt(session: Session, user: User) -> None:
    '''
    Calculates how long the account should be locked
    for and records the failed attempt.

    session (Session): the connection to the database
    user (User): single row of the specified users data

    return (None):
    '''

    failed_count = get_failed_attempts(session, user)

    current_time = datetime.now(timezone.utc).timestamp()
    expires_at = int(2 ** (failed_count ** 1.1)) * 60

    failed_login = UserLoginAttempts(
        user_id=user.id,
        failed_datetime=current_time,
        expires=current_time + (expires_at * 8)
    )

    user.failed_login_attempts += 1

    if failed_count > ATTEMPTS_BEFORE_LOCK:
        user.account_locked_until = current_time + expires_at
        user.user_status = 'Locked'

    session.add(failed_login)
    session.commit()
    session.refresh(failed_login)


def get_failed_attempts(session: Session, user: User) -> int:
    '''
    This function gets all the recorded attempts to access the account.
    If it finds any that have expired, they are automatically
    removed from the database and not counted.

    session (Session): the connection to the database
    user (User): single row of the specified users data

    return (int): total number of in-date failed attempts
    '''

    recorded_attempts = session.query(UserLoginAttempts).filter(UserLoginAttempts.user_id == user.id).all()

    total_attempts = len(recorded_attempts)
    current_time = datetime.now(timezone.utc).timestamp()
    deleted = False

    for attempt in recorded_attempts:
        if attempt.expires < current_time:
            session.delete(attempt)

            total_attempts -= 1
            user.failed_login_attempts -= 1

            deleted = True

    if deleted:
        session.commit()

    return total_attempts


def unlock_account(session: Session, user: User) -> bool:
    '''
    Checks whether the account is locked and the locked_until timer has expired.

    session (Session): the connection to the database
    user (User): single row of the specified users data

    return (bool): unlock account flag
    '''

    get_failed_attempts(session, user)

    current_time = datetime.now(timezone.utc).timestamp()
    unlocked = True

    if user.account_locked_until < current_time:
        if user.user_status == 'Locked':
            user.user_status = 'Inactive'

            session.commit()

    else:
        unlocked = False

    return unlocked
