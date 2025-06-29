'''
Routes from HTTP requests to the account gRPC server.
This file holds the routes for all authentication of
a user within the gateway API server.
'''

import json

from fastapi import APIRouter, Response, Cookie, Depends
from functools import partial
from pydantic import BaseModel

from src.backend_services.common.gRPC.server_connection import ServerCommunication
from src.backend_services.common.gRPC.data_conversion import get_session_response_data, \
    get_status_response_data, get_user_response_data
from src.backend_services.common.proto import user_login_pb2
from src.backend_services.common.proto.user_login_pb2_grpc import UserAuthServiceStub
from src.backend_services.common.redis.fetch_session_data import get_session_user_data

from src.backend_services.user_api_gateway.v1.middleware.account import is_user_logged_in
from src.backend_services.user_api_gateway.v1.routes.account.actions import router as settings_router
from src.backend_services.user_api_gateway.v1.utils.get_clients import get_grpc_account_client


router = APIRouter(prefix='/account')
router.include_router(settings_router, prefix="/settings")


class RegisterRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''

    email: str
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str


class LoginRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''

    email: str
    password: str


class OTPEmailRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''
    
    email: str
    otp_code: str
    return_action: str


@router.post('/register')
async def register_user(request_data: RegisterRequest, response: Response, client: ServerCommunication = Depends(get_grpc_account_client)) -> dict:
    '''
    Attempts to register a new user using the data provided by the client.
    Newly created accounts need to be verified before use.

    request_data (LoginRequest): class containing all the expected inputs from the client
    response (Response): the response object FastAPI send to the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]

    return (dict): returns a dict containing the response data
    '''

    data = user_login_pb2.UserRegistrationRequest(
        email=request_data.email,
        password=request_data.password,
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        date_of_birth=request_data.date_of_birth,
        gender=request_data.gender
    )

    success, data = client.grpc_request('UserRegistration', partial(UserAuthServiceStub), data)

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

    response.set_cookie(key="user", value=json.dumps(user), httponly=True)

    return { 'status': http_status, 'user': user }


@router.post('/login')
async def login_user(request_data: LoginRequest, response: Response, client: ServerCommunication = Depends(get_grpc_account_client)) -> dict:
    '''
    Attempts to log in the client to the account with
    the specified account details provided.

    request_data (LoginRequest): class containing all the expected inputs from the client
    response (Response): the response object FastAPI send to the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]

    return (dict): returns a dict containing the response data
    '''

    data = user_login_pb2.UserLoginRequest(
        email=request_data.email,
        password=request_data.password
    )

    success, data = client.grpc_request('UserLogin', partial(UserAuthServiceStub), data)

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
    session = get_session_response_data(data) if data.HasField('session') else None

    response.set_cookie(key="user", value=json.dumps(user), httponly=True)
    response.set_cookie(key="session", value=json.dumps(session), httponly=True)

    return { 'status': http_status, 'user': user, 'session': session, 'otp_required': data.otp_required }


@router.post('/verification/otp/email')
async def otp_verification(
    request_data: OTPEmailRequest,
    response: Response,
    client: ServerCommunication = Depends(get_grpc_account_client),
    session: str = Cookie(default=None)
    ) -> dict:

    '''
    Verifies the otp code sent by the client to verify the account.
    Sets cookies regarding the account specified by the client.

    request_data (OTPEmailRequest): class containing all the expected inputs from the client
    response (Response): the response object FastAPI send to the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    if session is None and request_data.return_action == 'LOGIN':
        return {
            'status': {
                'success': False,
                'http_status': 401,
                'message': 'Session Not Found. Please Log In'
            }
        }

    session_uuid = None

    try:
        if session is not None:
            session_dict = json.loads(session)

            if request_data.return_action == 'LOGIN':
                session_uuid = session_dict.get('session_uuid', None)

    except (json.JSONDecodeError, TypeError):
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': 'Cookies Provided Incorrectly Formatted'
            }
        }

    data = user_login_pb2.OTPRequest(
        email=request_data.email,
        otp_code=request_data.otp_code,
        session_uuid=session_uuid,
        return_action=request_data.return_action
    )

    success, data = client.grpc_request('OTPVerification', partial(UserAuthServiceStub), data)

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
    session = get_session_response_data(data) if data.HasField('session') else None

    if http_status['success']:
        response.set_cookie(key="user", value=json.dumps(user), httponly=True)
        response.set_cookie(key="session", value=json.dumps(session), httponly=True)

    return { 'status': http_status, 'user': user, 'session': session, 'otp_required': data.otp_required }


@router.post('/logout', dependencies=[Depends(is_user_logged_in)])
async def logout_user(
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client),
        session: str = Cookie(default=None),
        user: str = Cookie(default=None)
    ) -> dict:

    '''
    Logs out a signed in user by accessing the
    account-service and updating the relevant cookies.
    Deletes the cookies related to the account when logged out.

    response (Response): the response object FastAPI send to the client
    client (ServerCommunication): the class object used to communicate to the specific server [default - account-service object]
    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (dict): returns a dict containing the response data
    '''

    if None in [session, user]:
        return {
            'status': {
                'success': False,
                'http_status': 401,
                'message': 'You Must Be Logged In To Logout'
            }
        }

    try:
        user_dict = json.loads(user)
        session_dict = json.loads(session)

    except json.JSONDecodeError:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': 'Cookies Provided Incorrectly Formatted'
            }
        }

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

    data = user_login_pb2.UserLogoutRequest(
        session_uuid=session_uuid,
        user_uuid=session_user_data.get('uuid')
    )

    success, data = client.grpc_request('UserLogout', partial(UserAuthServiceStub), data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable',
                'service_response': get_status_response_data(data, embedded=False)
            }
        }

    response.delete_cookie(key="user")
    response.delete_cookie(key="session")

    return get_status_response_data(data, embedded=False)
