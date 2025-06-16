'''
This file holds all the functions in regards to otp generation and verification.
'''

import os
import pyotp
import uuid

from typing import Tuple

from src.backend_services.common.redis.redis import get_redis_conn


OTP_SECRET = os.environ.get("OTP_SECRET")


def create_otp() -> Tuple[str, int]:
    '''
    This function generates a random OTP code and id.
    The OTP code can only be verified by the correct OTP ID.

    return (str, int): returns the otp code and identification.
    '''

    otp_id = uuid.uuid4().int
    hotp = pyotp.HOTP(OTP_SECRET, digits=6)
    code = hotp.at(otp_id)

    return code, otp_id


def verify_otp(code: str, otp_id: int) -> Tuple[bool, str]:
    '''
    Verifies the OTP code by using an OTP ID.

    code (str): the code sent by the user
    otp_id (int): the ID sent by the server

    return (bool, str): success flag and message
    '''

    hotp = pyotp.HOTP(OTP_SECRET)

    if not hotp.verify(code, otp_id):
        return False, 'Invalid OTP Code Provided'

    return True, ''


def verify_otp_code(email: str, code: str) -> Tuple[bool, int, str, bool]:
    '''
    Receives the users email and OTP code, fetches
    the relevant OTP ID and verifies the code.

    email (str): the users email
    code (str): the provided OTP code

    return (bool, int, str, bool): success flag, http status, message and resend otp email flag
    '''

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, 500, message, False
    
    otp_id = redis_client.get(name=f'verification:otp:{email}')

    if otp_id is None:
        return False, 400, 'OTP Code Timed Out. Renewing Verification Email', True

    success, message = verify_otp(code, int(otp_id))

    return success, 200, message, False
