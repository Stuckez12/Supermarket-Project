'''
Contains the gateway routes to the account-service
in relation to account modifications.
'''

import json

from fastapi import APIRouter, Response, Cookie, Depends
from functools import partial
from pydantic import BaseModel

from src.backend_services.common.gRPC.data_conversion import get_status_response_data, get_user_response_data
from src.backend_services.common.gRPC.server_connection import ServerCommunication
from src.backend_services.common.proto import user_actions_pb2
from src.backend_services.common.proto.user_actions_pb2_grpc import UserSettingsServiceStub
from src.backend_services.common.redis.fetch_session_data import get_session_user_data

from src.backend_services.user_api_gateway.v1.middleware.account import is_user_logged_in
from src.backend_services.user_api_gateway.v1.utils.get_clients import get_grpc_account_client


router = APIRouter()


class ChangeEmailRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''

    new_email: str


class ChangePasswordRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''

    current_password: str
    new_password: str


class ChangeDetailsRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''

    first_name: str
    last_name: str
    gender: str
    date_of_birth: str


@router.get('/fetch-data', dependencies=[Depends(is_user_logged_in)])
async def fetch_user_data(
        client: ServerCommunication = Depends(get_grpc_account_client),
        session: str = Cookie(),
        user: str = Cookie()
    ) -> dict:

    '''
    Fetches the users data from the account-service and returns it as a dictionary.

    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    session_dict = json.loads(session)
    user_dict = json.loads(user)

    session_uuid = session_dict.get('session_uuid')
    user_uuid = user_dict.get('uuid')

    success, message, session_user_data = get_session_user_data(session_uuid, user_uuid)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': message
            }
        }

    data = user_actions_pb2.GetBasicAccountDetailsRequest(
        user_uuid=session_user_data.get('uuid')
    )

    success, data = client.grpc_request('GetBasicAccountData', partial(UserSettingsServiceStub), data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable',
                'service_response': get_status_response_data(data, embedded=False)
            }
        }

    http_status = get_status_response_data(data)
    user = get_user_response_data(data) if data.HasField('user') else None

    return { 'status': http_status, 'user': user }


@router.post('/change-email', dependencies=[Depends(is_user_logged_in)])
async def change_user_email(
        request_data: ChangeEmailRequest,
        client: ServerCommunication = Depends(get_grpc_account_client),
        session: str = Cookie(),
        user: str = Cookie()
    ) -> dict:

    '''
    Changes the users email to the new provided email.
    When this change occurs, the user is required to
    verify their email/account before being able to
    use their account.

    request_data (ChangeEmailRequest): class containing all the expected inputs from the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    session_dict = json.loads(session)
    user_dict = json.loads(user)

    session_uuid = session_dict.get('session_uuid')
    user_uuid = user_dict.get('uuid')

    success, message, session_user_data = get_session_user_data(session_uuid, user_uuid)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': message
            }
        }

    data = user_actions_pb2.UpdateUserEmailRequest(
        session_uuid=session_uuid,
        user_uuid=session_user_data.get('uuid'),
        current_email=session_user_data.get('email'),
        new_email=request_data.new_email
    )

    success, data = client.grpc_request('UpdateUserEmail', partial(UserSettingsServiceStub), data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable',
                'service_response': get_status_response_data(data, embedded=False)
            }
        }

    http_status = get_status_response_data(data)

    return { 'status': http_status, 'otp_required': data.otp_required }


@router.post('/change-password', dependencies=[Depends(is_user_logged_in)])
async def change_user_password(
        request_data: ChangePasswordRequest,
        client: ServerCommunication = Depends(get_grpc_account_client),
        session: str = Cookie(),
        user: str = Cookie()
    ) -> dict:

    '''
    Changes the users password to the new provided password.
    The user must type their current password before they
    can change their password.

    request_data (ChangePasswordRequest): class containing all the expected inputs from the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    session_dict = json.loads(session)
    user_dict = json.loads(user)

    session_uuid = session_dict.get('session_uuid')
    user_uuid = user_dict.get('uuid')

    success, message, session_user_data = get_session_user_data(session_uuid, user_uuid)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': message
            }
        }

    data = user_actions_pb2.UpdateUserPasswordRequest(
        user_uuid=session_user_data.get('uuid'),
        email=session_user_data.get('email'),
        current_password=request_data.current_password,
        new_password=request_data.new_password
    )

    success, data = client.grpc_request('UpdateUserPassword', partial(UserSettingsServiceStub), data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable',
                'service_response': get_status_response_data(data, embedded=False)
            }
        }

    http_status = get_status_response_data(data, embedded=False)

    return { 'status': http_status }


@router.post('/change-details', dependencies=[Depends(is_user_logged_in)])
async def change_user_details(
        request_data: ChangeDetailsRequest,
        client: ServerCommunication = Depends(get_grpc_account_client),
        session: str = Cookie(),
        user: str = Cookie()
    ) -> dict:

    '''
    Changes the select few details about the user. If the
    data is to not be changed, then a blank string must be
    provided. If unable to provide nothing, send the current
    data that is saved already in the database.

    request_data (ChangeDetailsRequest): class containing all the expected inputs from the client
    response (Response): the response object FastAPI send to the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    session_dict = json.loads(session)
    user_dict = json.loads(user)

    session_uuid = session_dict.get('session_uuid')
    user_uuid = user_dict.get('uuid')

    success, message, session_user_data = get_session_user_data(session_uuid, user_uuid)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': message
            }
        }

    data = user_actions_pb2.UpdateUserDetailsRequest(
        user_uuid=session_user_data.get('uuid'),
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        gender=request_data.gender,
        date_of_birth=request_data.date_of_birth
    )

    success, data = client.grpc_request('UpdateUserDetails', partial(UserSettingsServiceStub), data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable',
                'service_response': get_status_response_data(data, embedded=False)
            }
        }

    http_status = get_status_response_data(data)
    user = get_user_response_data(data) if data.HasField('user') else None

    return { 'status': http_status, 'user': user }


@router.delete('/delete-account', dependencies=[Depends(is_user_logged_in)])
async def delete_user_account(
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client),
        session: str = Cookie(),
        user: str = Cookie()
    ) -> dict:

    '''
    Deletes the account that the user is currently logged in as.
    The user data is deleted but the account remains with no
    identifying data related to the user. This is done to preserve
    all the necessary actions that can be used for various data
    analysis methods.

    response (Response): the response object FastAPI send to the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    session_dict = json.loads(session)
    user_dict = json.loads(user)

    session_uuid = session_dict.get('session_uuid')
    user_uuid = user_dict.get('uuid')

    success, message, session_user_data = get_session_user_data(session_uuid, user_uuid)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': message
            }
        }

    data = user_actions_pb2.DeleteAccountRequest(
        user_uuid=session_user_data.get('uuid')
    )

    success, data = client.grpc_request('DeleteAccount', partial(UserSettingsServiceStub), data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable',
                'service_response': get_status_response_data(data, embedded=False)
            }
        }

    http_status = get_status_response_data(data, embedded=False)
    
    response.delete_cookie(key="user")
    response.delete_cookie(key="session")

    return { 'status': http_status }
