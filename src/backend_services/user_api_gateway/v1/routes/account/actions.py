'''

'''

import json

from fastapi import APIRouter, Response, Cookie, Depends
from functools import partial
from pydantic import BaseModel

from src.backend_services.common.gRPC.data_conversion import get_status_response_data, get_user_response_data
from src.backend_services.common.gRPC.server_connection import ServerCommunication
from src.backend_services.common.proto import user_actions_pb2
from src.backend_services.common.proto.user_actions_pb2_grpc import UserSettingsServiceStub

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
        user: str = Cookie()
    ) -> dict:

    '''

    '''

    user_dict = json.loads(user)

    data = user_actions_pb2.GetBasicAccountDetailsRequest(
        user_uuid=user_dict.get('uuid')
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
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client),
        user: str = Cookie()
    ) -> dict:

    '''

    '''

    user_dict = json.loads(user)

    data = user_actions_pb2.UpdateUserEmailRequest(
        user_uuid=user_dict.get('uuid'),
        current_email=user_dict.get('email'),
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
    user = get_user_response_data(data) if data.HasField('user') else None

    if user is not None:
        response.set_cookie(key="user", value=json.dumps(user), httponly=True)

    return { 'status': http_status, 'user': user }


@router.post('/change-password', dependencies=[Depends(is_user_logged_in)])
async def change_user_password(
        request_data: ChangePasswordRequest,
        client: ServerCommunication = Depends(get_grpc_account_client),
        user: str = Cookie()
    ) -> dict:

    '''

    '''

    user_dict = json.loads(user)

    data = user_actions_pb2.UpdateUserPasswordRequest(
        user_uuid=user_dict.get('uuid'),
        email=user_dict.get('email'),
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

    http_status = get_status_response_data(data)

    return { 'status': http_status }


@router.post('/change-details', dependencies=[Depends(is_user_logged_in)])
async def change_user_details(
        request_data: ChangeDetailsRequest,
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client),
        user: str = Cookie()
    ) -> dict:

    '''

    '''

    user_dict = json.loads(user)

    data = user_actions_pb2.UpdateUserDetailsRequest(
        user_uuid=user_dict.get('uuid'),
        email=user_dict.get('email'),
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

    if user is not None:
        response.set_cookie(key="user", value=json.dumps(user), httponly=True)

    return { 'status': http_status, 'user': user }


@router.delete('/delete-account', dependencies=[Depends(is_user_logged_in)])
async def delete_user_account(
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client),
        user: str = Cookie()
    ) -> dict:

    '''

    '''

    user_dict = json.loads(user)

    data = user_actions_pb2.DeleteAccountRequest(
        user_uuid=user_dict.get('uuid'),
        email=user_dict.get('email')
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

    http_status = get_status_response_data(data)
    
    response.delete_cookie(key="user")
    response.delete_cookie(key="session")

    return { 'status': http_status }
