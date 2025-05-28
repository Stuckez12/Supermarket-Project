import grpc
import json
import os
import uuid

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from src.backend_services.account.database.database import get_db_conn
from src.backend_services.account.database.models import User, UserLoginAttempts

from src.backend_services.common.email.email_functions import generate_otp_email
from src.backend_services.common.email.otp_functions import verify_otp_code
from src.backend_services.common.proto import user_login_pb2, user_login_pb2_grpc
from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response
from src.backend_services.common.redis.redis import get_redis_conn
from src.backend_services.common.redis.user_sessions import create_session, update_session, delete_session
from src.backend_services.common.utils.data_verification import DataVerification
from src.backend_services.common.utils.schema import load_yaml_file_as_dict, get_verification_schema
from src.backend_services.common.utils.utils import user_proto_format


# Global config
AUTH_VERIFY_CONFIG = None
OTP_VERIFY_CONFIG = None
LOGOUT_VERIFY_CONFIG = None

# environment variables
ATTEMPTS_BEFORE_LOCK = os.environ.get('ACCOUNT_MAX_LOGIN_ATTEMPTS')


def reconfigure_adaptive_restrictions(): # TEMPORARY
    global AUTH_VERIFY_CONFIG

    today = datetime.today()

    min_date = today.replace(year=today.year - 110).strftime("%Y-%m-%d")
    max_date = today.replace(year=today.year - 9).strftime("%Y-%m-%d")

    AUTH_VERIFY_CONFIG['date_of_birth']['restrictions']['date']['min'] = min_date
    AUTH_VERIFY_CONFIG['date_of_birth']['restrictions']['date']['max'] = max_date


def initialise_file():
    schemas = load_yaml_file_as_dict("src/backend_services/account/verification_config/user_auth.yaml")

    global AUTH_VERIFY_CONFIG
    AUTH_VERIFY_CONFIG = schemas['auth']

    global OTP_VERIFY_CONFIG
    OTP_VERIFY_CONFIG = schemas['otp']

    global LOGOUT_VERIFY_CONFIG
    LOGOUT_VERIFY_CONFIG = schemas['logout']


initialise_file()


def send_and_store_otp_code(email, return_status, replace_message=True):
    '''
    
    '''

    success, otp_id, message = generate_otp_email([email])

    if not success:
        return_status.success = False
        return_status.http_status = 500

        if replace_message:
            return_status.message = 'Unable To Send Verification Email'

        else:
            return_status.message = message
            return_status.error.extend(['Unable To Send Verification Email'])

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)

    success, message, redis_client = get_redis_conn()

    if not success:
        return_status.success = False
        return_status.http_status = 500
        
        if replace_message:
            return_status.message = 'Unable To Connect To Redis Service'

        else:
            return_status.error.extend(['Unable To Connect To Redis Service'])

        return_status.error.extend([message])

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)

    redis_client.set(
        name=f'verification:otp:{email}',
        value=otp_id,
        ex=600  # 10 minutes
    )

    # Testing purposes only for print statement
    print('Fetched Code From Redis:', redis_client.get(f'verification:otp:{email}'))

    return True, None


def check_email_session_data(email, session_uuid, return_status):
    '''
    
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

    if user_session_data['email'] != email:
        return_status.success = False
        return_status.http_status = 400
        return_status.message = 'Logged In Account Mismatch With Provided Email'

        return False, user_login_pb2.UserRegistrationResponse(status=return_status)
    
    return True, None


def iter_failed_attempt(session: Session, user: User):
    '''
    
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

    
def get_failed_attempts(session: Session, user: User):
    '''
    This function gets all the recorded attempts to access the account.
    If it finds any that have expired, they are automatically
    removed from the database and not counted.

    session (Session): the connection to the database
    user (User): the specified user (user row data)

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


def unlock_account(session: Session, user: User):
    '''
    
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


class UserAuthentication_Service(user_login_pb2_grpc.UserAuthService):
    '''
    This class holds all the grpc requests on the server side
    in regards to user login and authentication.
    '''


    def UserRegistration(self, request: user_login_pb2.UserRegistrationRequest, context: grpc.ServicerContext) -> user_login_pb2.UserRegistrationResponse:
        '''
        This gRPC function recieves registration details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.
        '''

        print("UserRegistration Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = {
            'email': request.email,
            'password': request.password,
            'first_name': request.first_name,
            'last_name': request.last_name,
            'gender': request.gender,
            'date_of_birth': request.date_of_birth,
        }

        reconfigure_adaptive_restrictions() # TEMP: remove when verification for said dates are restricted adaptively

        success, message, schema = get_verification_schema(AUTH_VERIFY_CONFIG, data)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

            return user_login_pb2.UserRegistrationResponse(status=return_status)

        success, errors = DataVerification().verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return user_login_pb2.UserRegistrationResponse(status=return_status)

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.email == request.email).first()

            if user_result is not None:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Email Already In Use'

                return user_login_pb2.UserRegistrationResponse(status=return_status)
            
            new_uuid = str(uuid.uuid4())

            while True:
                uuid_result = session.query(User).filter(User.uuid == new_uuid).first()

                if uuid_result is None:
                    break

                new_uuid = str(uuid.uuid4())

            register_user = User(
                uuid = new_uuid,
                email = request.email,
                password = generate_password_hash(request.password),
                first_name = request.first_name,
                last_name = request.last_name,
                gender = request.gender,
                date_of_birth = request.date_of_birth
            )

            session.add(register_user)
            session.commit()
            session.refresh(register_user)

        success, return_message = send_and_store_otp_code(request.email, return_status)

        if not success:
            return return_message

        return user_login_pb2.UserRegistrationResponse(status=return_status)


    def UserLogin(self, request: user_login_pb2.UserLoginRequest, context: grpc.ServicerContext) -> user_login_pb2.UserLoginResponse:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.
        '''

        print("UserLogin Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = {
            'email': request.email,
            'password': request.password,
        }
        success, message, schema = get_verification_schema(AUTH_VERIFY_CONFIG, data)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

            return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)

        success, errors = DataVerification().verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.email == request.email).first()

            if user_result is None:
                return_status.success = False
                return_status.http_status = 400
                return_status.message = 'No Account Associated With Given Email'

                return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)

            if not user_result.is_accessible():
                return_status.success = False
                return_status.http_status = 403

                pass_through = False

                if user_result.user_status == 'Closed':
                    return_status.message = 'This Account Has Been Closed'
                    return_status.error.extend(['Account Data Will Be Wiped In The Near Future Following TOS'])

                elif user_result.user_status == 'Terminated':
                    return_status.message = 'This Account Has Been Disabled'

                elif user_result.user_status == 'Locked':
                    pass_through = unlock_account(session, user_result)

                    if not pass_through:
                        return_status.message = 'This Account Is Temporarily Locked. Please Try Again Later'

                if not pass_through:
                    return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)

            if user_result is None or not check_password_hash(user_result.password, request.password):
                return_status.success = False
                return_status.http_status = 403
                return_status.message = 'Email Or Password Incorrect'

                iter_failed_attempt(session, user_result)

                return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)
            
            user_result.last_login = datetime.now(timezone.utc).timestamp()
            session.commit()

            session_uuid, expiry = create_session(user_result.uuid, user_result)

            user_session = user_login_pb2.UserSession(
                session_uuid=session_uuid,
                expiry_time=expiry
            )

            otp_required = False

            if not user_result.is_verified():
                return_status.success = False
                return_status.http_status = 403
                return_status.message = 'Account Not Verified'

                otp_required = True

                success, return_message = send_and_store_otp_code(request.email, return_status)

                if not success:
                    return return_message

            user = user_proto_format(user_result)

            return user_login_pb2.UserLoginResponse(
                status=return_status,
                user=user,
                session=user_session,
                otp_required=otp_required
            )


    def OTPVerification(self, request: user_login_pb2.OTPRequest, context: grpc.ServicerContext) -> user_login_pb2.UserLoginResponse:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.
        '''

        print("OTPVerification Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=201, # 202 for logging in
            message='Request Successful'
        )

        data = {
            'email': request.email,
            'otp_code': request.otp_code,
            'session_uuid': request.session_uuid,
            'return_action': request.return_action
        }
        success, message, schema = get_verification_schema(OTP_VERIFY_CONFIG, data)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

            return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)

        success, errors = DataVerification().verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return user_login_pb2.UserLoginResponse(status=return_status, otp_required=False)

        if request.return_action == 'LOGIN':
            success, message = check_email_session_data(request.email, request.session_uuid, return_status)

            if not success:
                return message

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.email == request.email).first()

            if not user_result:
                return_status.success = False
                return_status.http_status = 400
                return_status.message = 'Email Is Not Linked To Any Account'

                return user_login_pb2.UserLoginResponse(status=return_status)
            
            if user_result.email_verified:
                return_status.success = False
                return_status.http_status = 400
                return_status.message = 'Email Has Already Been Verified'

                return user_login_pb2.UserLoginResponse(status=return_status)

            success, http_status, message, resend_otp_email = verify_otp_code(request.email, request.otp_code)
            
            if not success:
                return_status.success = False
                return_status.http_status = http_status
                return_status.message = message

                if resend_otp_email:
                    success, return_message = send_and_store_otp_code(request.email, return_status, replace_message=False)

                    if not success:
                        return return_message
                    
                return user_login_pb2.UserLoginResponse(status=return_status)

            user_result.email_verified = True
            user_result.user_status = 'Inactive'

            session.commit()

            user = user_proto_format(user_result)
            user_session = None

            if request.return_action == 'LOGIN':
                session_uuid, expiry = update_session(request.session_uuid, user_result.uuid, user_result)

                user_session = user_login_pb2.UserSession(
                    session_uuid=session_uuid,
                    expiry_time=expiry
                )
                
                return_status.http_status = 202

                if not success:
                    return_status.success = False
                    return_status.http_status = 500
                    return_status.message = message

                    return user_login_pb2.UserLoginResponse(status=return_status)

        return user_login_pb2.UserLoginResponse(status=return_status, user=user, session=user_session, otp_required=False)


    def UserLogout(self, request: user_login_pb2.UserLogoutRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.
        '''

        print("OTPVerification Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = {
            'session_uuid': request.session_uuid,
            'user_uuid': request.user_uuid
        }
        success, message, schema = get_verification_schema(LOGOUT_VERIFY_CONFIG, data)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

            return return_status
        
        success, errors = DataVerification().verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return return_status
        
        success, message = delete_session(request.session_uuid, request.user_uuid)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

        return return_status
