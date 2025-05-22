import os
import pyotp
import uuid


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
