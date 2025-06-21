'''
This file holds all of the actions that account
users can perform on the gRPC account-service.
These actions will be seen in the settings tab
for the frontend.
'''

import grpc

from datetime import datetime, timezone, UTC
from typing import Self
from werkzeug.security import check_password_hash, generate_password_hash

from src.backend_services.account.authentication.login_funcs import send_and_store_otp_code
from src.backend_services.account.database.database import get_db_conn
from src.backend_services.account.database.models import User

from src.backend_services.common.proto import user_actions_pb2, user_actions_pb2_grpc
from src.backend_services.common.proto.user_actions_pb2 import BasicAccountDetailsResponse
from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response, OTP_Response
from src.backend_services.common.redis.fetch_session_data import update_user_email_session
from src.backend_services.common.utils.data_verification import DataVerification
from src.backend_services.common.utils.schema import load_yaml_file_as_dict, get_verification_schema
from src.backend_services.common.utils.utils import user_proto_format


# Global config
BASIC_VERIFY_CONFIG = None
UPDATE_EMAIL_VERIFY_CONFIG = None
UPDATE_PASSWORD_VERIFY_CONFIG = None
UPDATE_DATA_VERIFY_CONFIG = None
DELETION_VERIFY_CONFIG = None


def reconfigure_adaptive_restrictions() -> None: # TEMPORARY
    '''
    Temporary function until future implementation of
    more advanced datetime checking.

    Changes the config file for authentication to use
    up to date time limits.

    return (None):
    '''

    global UPDATE_DATA_VERIFY_CONFIG

    today = datetime.today()

    min_date = today.replace(year=today.year - 110).strftime("%Y-%m-%d")
    max_date = today.replace(year=today.year - 9).strftime("%Y-%m-%d")

    UPDATE_DATA_VERIFY_CONFIG['date_of_birth']['restrictions']['date']['min'] = min_date
    UPDATE_DATA_VERIFY_CONFIG['date_of_birth']['restrictions']['date']['max'] = max_date


def initialise_file() -> None:
    '''
    When the server is executed, the file fetches the
    verification config and stores it in memory.

    return (None):
    '''

    schemas = load_yaml_file_as_dict("src/backend_services/account/verification_config/user_action.yaml")

    global BASIC_VERIFY_CONFIG
    BASIC_VERIFY_CONFIG = schemas['basic_data']

    global UPDATE_EMAIL_VERIFY_CONFIG
    UPDATE_EMAIL_VERIFY_CONFIG = schemas['update_email']

    global UPDATE_PASSWORD_VERIFY_CONFIG
    UPDATE_PASSWORD_VERIFY_CONFIG = schemas['update_password']

    global UPDATE_DATA_VERIFY_CONFIG
    UPDATE_DATA_VERIFY_CONFIG = schemas['update_data']

    global DELETION_VERIFY_CONFIG
    DELETION_VERIFY_CONFIG = schemas['delete_account']


initialise_file()


class UserAction_Service(user_actions_pb2_grpc.UserSettingsService):
    '''
    This class holds all the gRPC requests on the server side
    in regards to user actions and events.
    '''


    def GetBasicAccountData(cls: Self, request: user_actions_pb2.GetBasicAccountDetailsRequest, context: grpc.ServicerContext) -> BasicAccountDetailsResponse:
        '''
        This gRPC function recieves a user uuid from the request.
        The data recieved is validated and data related to the user and return the users' data.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (GetBasicAccountDetailsRequest): the specified proto defined request message for the rpc call

        return (BasicAccountDetailsResponse): the proto Message response including user data and request status
        '''

        print("GetBasicAccountData Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = { 'uuid': request.user_uuid }

        success, message, schema = get_verification_schema(BASIC_VERIFY_CONFIG, data)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

            return BasicAccountDetailsResponse(status=return_status)

        success, errors = DataVerification().verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return BasicAccountDetailsResponse(status=return_status)

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.uuid == request.user_uuid).first()

            if user_result is None:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Unable To Fetch Account Data'

                return BasicAccountDetailsResponse(status=return_status)

            user = user_proto_format(user_result)

            return BasicAccountDetailsResponse(status=return_status, user=user)


    def UpdateUserEmail(cls: Self, request: user_actions_pb2.UpdateUserEmailRequest, context: grpc.ServicerContext) -> OTP_Response:
        '''
        This gRPC function recieves a user uuid and the new email from the request.
        The data recieved is validated and the data is updated on the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (UpdateUserEmailRequest): the specified proto defined request message for the rpc call

        return (OTP_Response): the proto Message response with the request status
        '''

        print("UpdateUserEmail Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = {
            'session_uuid': request.session_uuid,
            'user_uuid': request.user_uuid,
            'current_email': request.current_email,
            'new_email': request.new_email
        }

        success, message, schema = get_verification_schema(UPDATE_EMAIL_VERIFY_CONFIG, data)

        if not success:
            return_status.success = False
            return_status.http_status = 500
            return_status.message = message

            return OTP_Response(status=return_status, otp_required=False)

        success, errors = DataVerification().verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return OTP_Response(status=return_status, otp_required=False)

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.uuid == request.user_uuid, User.email == request.current_email).first()

            if user_result is None:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Unable To Fetch Account Data'

                return OTP_Response(status=return_status, otp_required=False)

            user_result.email = request.new_email
            user_result.email_verified = False
            user_result.user_status = 'Unverified'

            success, message = update_user_email_session(request.session_uuid, request.user_uuid, request.new_email, False)

            if not success:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Unable To Fetch Account Data'

                return OTP_Response(status=return_status, otp_required=False)

            success, return_message = send_and_store_otp_code(request.new_email, return_status)

            if not success:
                return OTP_Response(status=return_message, otp_required=True)

            user_result.last_activity_at = datetime.now(timezone.utc).timestamp()

            session.commit()

            return OTP_Response(status=return_status, otp_required=True)


    def UpdateUserPassword(cls: Self, request: user_actions_pb2.UpdateUserPasswordRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves a user uuid and the new password from the request.
        The data recieved is validated and the data is updated on the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (UpdateUserPasswordRequest): the specified proto defined request message for the rpc call

        return (HTTP_Response): the proto Message response with the request status
        '''

        print("UpdateUserPassword Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = {
            'user_uuid': request.user_uuid,
            'email': request.email,
            'current_password': request.current_password,
            'new_password': request.new_password
        }

        success, message, schema = get_verification_schema(UPDATE_EMAIL_VERIFY_CONFIG, data)

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

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.uuid == request.user_uuid, User.email == request.email).first()

            if user_result is None:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Unable To Fetch Account Data'

                return return_status

            if not check_password_hash(user_result.password, request.current_password):
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Incorrect Password Provided'

                return return_status

            if request.current_password == request.new_password:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'New Password Cannot Be The Same As The Current Password'

                return return_status

            user_result.password = generate_password_hash(request.new_password)
            user_result.last_activity_at = datetime.now(timezone.utc).timestamp()

            session.commit()

            return return_status


    def UpdateUserDetails(cls: Self, request: user_actions_pb2.UpdateUserDetailsRequest, context: grpc.ServicerContext) -> BasicAccountDetailsResponse:
        '''
        This gRPC function recieves a user uuid and the specified data they want to modify from the request.
        The data recieved is validated and data related to the user and return the users' data.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (UpdateUserDetailsRequest): the specified proto defined request message for the rpc call

        return (BasicAccountDetailsResponse): the proto Message response including user data and request status
        '''

        print("UpdateUserDetails Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = {
            'user_uuid': request.user_uuid,
            'first_name': request.first_name,
            'last_name': request.last_name,
            'gender': request.gender,
            'date_of_birth': request.date_of_birth
        }

        reconfigure_adaptive_restrictions() # TODO: remove when verification for said dates are restricted adaptively

        success, message, schema = get_verification_schema(UPDATE_EMAIL_VERIFY_CONFIG, data)

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

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.uuid == request.user_uuid).first()

            if user_result is None:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Unable To Fetch Account Data'

                return return_status
            
            # TODO: Simplify this if statement block
            if request.first_name != '':
                user_result.first_name = request.first_name

            if request.last_name != '':
                user_result.last_name = request.last_name

            if request.gender != '':
                user_result.gender = request.gender

            if request.date_of_birth != '':
                user_result.date_of_birth = request.date_of_birth

            user_result.last_activity_at = datetime.now(timezone.utc).timestamp()

            session.commit()
            user = user_proto_format(user_result)

            return BasicAccountDetailsResponse(status=return_status, user=user)


    def DeleteAccount(cls: Self, request: user_actions_pb2.DeleteAccountRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves a user uuid from the request.
        The data recieved is validated and deletes the users' data from the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (DeleteAccountRequest): the specified proto defined request message for the rpc call

        return (HTTP_Response): the proto Message response including user data and request status
        '''

        print("DeleteAccount Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )

        data = { 'uuid': request.user_uuid }

        success, message, schema = get_verification_schema(DELETION_VERIFY_CONFIG, data)

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

        with get_db_conn() as session:
            user_result = session.query(User).filter(User.uuid == request.user_uuid).first()

            if user_result is None:
                return_status.success = False
                return_status.http_status = 401
                return_status.message = 'Unable To Fetch Account Data'

                return return_status
            
            user_result.email = ''
            user_result.password = ''
            
            user_result.first_name = ''
            user_result.last_name = ''
            user_result.gender = 'DELETED'
            user_result.date_of_birth = datetime.now(UTC)

            user_result.user_status = 'Closed'
            user_result.last_activity_at = datetime.now(timezone.utc).timestamp()

            session.commit()

            return return_status
