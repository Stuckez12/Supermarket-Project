'''
This file holds the generic authentication for a user on the gRPC account-service
'''

import grpc
import os
import uuid

from datetime import datetime, timezone
from typing import Self
from werkzeug.security import check_password_hash, generate_password_hash

from src.backend_services.account.authentication.login_funcs import check_email_session_data, \
    send_and_store_otp_code, unlock_account, iter_failed_attempt
from src.backend_services.account.database.database import get_db_conn
from src.backend_services.account.database.models import User

from src.backend_services.common.email.otp_functions import verify_otp_code
from src.backend_services.common.proto import user_login_pb2, user_login_pb2_grpc
from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response
from src.backend_services.common.redis.user_sessions import create_session, update_session, delete_session
from src.backend_services.common.utils.data_verification import DataVerification
from src.backend_services.common.utils.schema import load_yaml_file_as_dict, get_verification_schema
from src.backend_services.common.utils.utils import user_proto_format


# Global config
AUTH_VERIFY_CONFIG = None
OTP_VERIFY_CONFIG = None
LOGOUT_VERIFY_CONFIG = None


def reconfigure_adaptive_restrictions() -> None: # TEMPORARY
    '''
    Temporary function until future implementation of
    more advanced datetime checking.

    Changes the config file for authentication to use
    up to date time limits.

    return (None):
    '''

    global AUTH_VERIFY_CONFIG

    today = datetime.today()

    min_date = today.replace(year=today.year - 110).strftime("%Y-%m-%d")
    max_date = today.replace(year=today.year - 9).strftime("%Y-%m-%d")

    AUTH_VERIFY_CONFIG['date_of_birth']['restrictions']['date']['min'] = min_date
    AUTH_VERIFY_CONFIG['date_of_birth']['restrictions']['date']['max'] = max_date


def initialise_file() -> None:
    '''
    When the server is executed, the file fetches the
    verification config and stores it in memory.

    return (None):
    '''

    schemas = load_yaml_file_as_dict("src/backend_services/account/verification_config/user_auth.yaml")

    global AUTH_VERIFY_CONFIG
    AUTH_VERIFY_CONFIG = schemas['auth']

    global OTP_VERIFY_CONFIG
    OTP_VERIFY_CONFIG = schemas['otp']

    global LOGOUT_VERIFY_CONFIG
    LOGOUT_VERIFY_CONFIG = schemas['logout']


initialise_file()


class UserAuthentication_Service(user_login_pb2_grpc.UserAuthService):
    '''
    This class holds all the gRPC requests on the server side
    in regards to user login and authentication.
    '''


    def UserRegistration(cls: Self, request: user_login_pb2.UserRegistrationRequest, context: grpc.ServicerContext) -> user_login_pb2.UserRegistrationResponse:
        '''
        This gRPC function recieves registration details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAuthentication_Service class
        request (OTPRequest): the specified proto defined request message for the rpc call

        return (UserRegistrationResponse): the proto Message response including user data and request status
        '''

        print("UserRegistration Request Made:")
        print(request)

        # TODO: Transfer all verification code to one adaptive function to be used for all RPC calls
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

        reconfigure_adaptive_restrictions() # TODO: remove when verification for said dates are restricted adaptively

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
            return user_login_pb2.UserLoginResponse(status=return_message)

        return user_login_pb2.UserRegistrationResponse(status=return_status)


    def UserLogin(cls: Self, request: user_login_pb2.UserLoginRequest, context: grpc.ServicerContext) -> user_login_pb2.UserLoginResponse:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAuthentication_Service class
        request (OTPRequest): the specified proto defined request message for the rpc call

        return (UserLoginResponse): the proto Message response including user data and request status
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
                    return user_login_pb2.UserLoginResponse(status=return_message)

            user = user_proto_format(user_result)

            return user_login_pb2.UserLoginResponse(
                status=return_status,
                user=user,
                session=user_session,
                otp_required=otp_required
            )


    def OTPVerification(cls: Self, request: user_login_pb2.OTPRequest, context: grpc.ServicerContext) -> user_login_pb2.UserLoginResponse:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAuthentication_Service class
        request (OTPRequest): the specified proto defined request message for the rpc call

        return (UserLoginResponse): the proto Message response including user data and request status
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
                        return user_login_pb2.UserLoginResponse(status=return_message)
                    
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


    def UserLogout(cls: Self, request: user_login_pb2.UserLogoutRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAuthentication_Service class
        request (UserLogoutRequest): the specified proto defined request message for the rpc call

        return (HTTP_Response): the basic proto Message response indicating a successful or failed request
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
