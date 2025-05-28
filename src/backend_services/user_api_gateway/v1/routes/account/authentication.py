import base64
import json

from fastapi import APIRouter, Response, Cookie, Depends
from pydantic import BaseModel

from src.backend_services.common.proto import user_login_pb2

from src.backend_services.user_api_gateway.v1.utils.get_clients import get_grpc_account_client

router = APIRouter()


class RegisterRequest(BaseModel):
    '''
    
    '''

    email: str
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str


class LoginRequest(BaseModel):
    '''
    
    '''

    email: str
    password: str


class OTPEmailRequest(BaseModel):
    '''
    
    '''
    
    email: str
    otp_code: str
    return_action: str


def get_status_response_data(data, embeded=True):
    '''
    
    '''

    if embeded:
        return {
            'success': data.status.success,
            'http_status': data.status.http_status,
            'message': data.status.message,
            'error': list(data.status.error)
        }

    return {
        'success': data.success,
        'http_status': data.http_status,
        'message': data.message,
        'error': list(data.error)
    }


def get_user_response_data(data):
    '''
    
    '''

    return {
        'uuid': data.user.uuid,
        'email': data.user.email,
        'password_last_changed_at': data.user.password_last_changed_at,
        'first_name': data.user.first_name,
        'last_name': data.user.last_name,
        'gender': data.user.gender,
        'date_of_birth': data.user.date_of_birth,
        'created_at': data.user.created_at,
        'updated_at': data.user.updated_at,
        'last_login': data.user.last_login,
        'email_verified': data.user.email_verified,
        'user_status': data.user.user_status,
        'user_role': data.user.user_role
    }


def get_session_response_data(data):
    '''
    
    '''

    return {
        'session_uuid': data.session.session_uuid,
        'expiry_time': data.session.expiry_time
    }


@router.post('/register')
async def register_user(request_data: RegisterRequest, response: Response, client = Depends(get_grpc_account_client)):
    '''
    
    '''

    data = user_login_pb2.UserRegistrationRequest(
        email=request_data.email,
        password=request_data.password,
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        date_of_birth=request_data.date_of_birth,
        gender=request_data.gender
    )

    success, data = client.grpc_request('UserRegistration', data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable'
            }
        }

    http_status = get_status_response_data(data)
    user = get_user_response_data(data) if data.HasField('user') else None

    response.set_cookie(key="user", value=json.dumps(user), httponly=True)

    return { 'status': http_status, 'user': user }


@router.post('/login')
async def login_user(request_data: LoginRequest, response: Response, client = Depends(get_grpc_account_client)):
    '''
    
    '''

    data = user_login_pb2.UserLoginRequest(
        email=request_data.email,
        password=request_data.password
    )

    success, data = client.grpc_request('UserLogin', data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable'
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
    client = Depends(get_grpc_account_client),
    session: str = Cookie(default=None)
    ):

    '''
    
    '''

    if session is None and request_data.return_action == 'LOGIN':
        return {
            'status': {
                'success': False,
                'http_status': 401,
                'message': 'Session Not Found. Please Log In'
            }
        }

    try:
        session_dict = json.loads(session)

    except json.JSONDecodeError:
        return {
            'status': {
                'success': False,
                'http_status': 400,
                'message': 'Cookies Provided Incorrectly Formatted'
            }
        }
    
    session_uuid = None
    
    if request_data.return_action == 'LOGIN':
        session_uuid = session_dict.get('session_uuid', None)

    data = user_login_pb2.OTPRequest(
        email=request_data.email,
        otp_code=request_data.otp_code,
        session_uuid=session_uuid,
        return_action=request_data.return_action
    )

    success, data = client.grpc_request('OTPVerification', data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable'
            }
        }

    http_status = get_status_response_data(data)
    user = get_user_response_data(data) if data.HasField('user') else None
    session = get_session_response_data(data) if data.HasField('session') else None

    if http_status['success']:
        response.set_cookie(key="user", value=json.dumps(user), httponly=True)
        response.set_cookie(key="session", value=json.dumps(session), httponly=True)

    return { 'status': http_status, 'user': user, 'session': session, 'otp_required': data.otp_required }


@router.post('/logout')
async def logout_user(
        response: Response,
        client = Depends(get_grpc_account_client),
        session: str = Cookie(default=None),
        user: str = Cookie(default=None)
    ):

    '''
    
    '''

    if None in [session, user]:
        return {
            'status': {
                'success': False,
                'http_status': 401,
                'message': 'You Must Be Logged In To Logout',
                'session': session,
                'user': user
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

    data = user_login_pb2.UserLogoutRequest(
        session_uuid=session_dict.get('session_uuid'),
        user_uuid=user_dict.get('uuid')
    )

    success, data = client.grpc_request('UserLogout', data)

    if not success:
        return {
            'status': {
                'success': False,
                'http_status': 502,
                'message': 'Service Unavailable'
            }
        }

    response.delete_cookie(key="user")
    response.delete_cookie(key="session")

    return get_status_response_data(data, embeded=False)
