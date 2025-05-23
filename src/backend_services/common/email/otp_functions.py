import os
import pyotp
import uuid

from src.backend_services.common.redis.redis import get_redis_conn


OTP_SECRET = os.environ.get("OTP_SECRET")


def create_otp():
    '''
    
    '''

    otp_id = uuid.uuid4().int
    hotp = pyotp.HOTP(OTP_SECRET, digits=6)
    code = hotp.at(otp_id)

    return code, otp_id


def verify_otp(code, otp_id):
    '''
    
    '''

    hotp = pyotp.HOTP(OTP_SECRET)

    if not hotp.verify(code, otp_id):
        return False, 'Invalid OTP Code Provided'

    return True, ''


def verify_otp_code(email, code):
    '''
    
    '''

    print('--------')

    success, message, redis_client = get_redis_conn()

    if not success:
        return False, 500, message, False
    
    print('Redis Client Got')
    
    otp_id = redis_client.get(name=f'verification:otp:{email}')

    if otp_id is None:
        return False, 400, 'OTP Code Timed Out. Renewing Verification Email', True
    
    print('Valid OTP ID Got')

    success, message = verify_otp(code, int(otp_id))

    print('OTP Verified?')

    return success, 200, message, False

     
