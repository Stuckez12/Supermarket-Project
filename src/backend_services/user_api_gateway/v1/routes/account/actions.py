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


class FetchUserDataRequest(BaseModel):
    '''
    The expected data to receive from the user.
    '''

    uuid: str


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
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client)
    ) -> dict:

    '''

    '''

    return {
        'status': {
            'success': True,
            'http_status': 200,
            'message': ''
        }
    }


@router.post('/change-password', dependencies=[Depends(is_user_logged_in)])
async def change_user_password(
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client)
    ) -> dict:

    '''

    '''

    return {
        'status': {
            'success': True,
            'http_status': 200,
            'message': ''
        }
    }


@router.post('/change-details', dependencies=[Depends(is_user_logged_in)])
async def change_user_details(
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client)
    ) -> dict:

    '''

    '''

    return {
        'status': {
            'success': True,
            'http_status': 200,
            'message': ''
        }
    }


@router.delete('/delete-account', dependencies=[Depends(is_user_logged_in)])
async def delete_user_account(
        response: Response,
        client: ServerCommunication = Depends(get_grpc_account_client)
    ) -> dict:

    '''

    '''

    return {
        'status': {
            'success': True,
            'http_status': 200,
            'message': ''
        }
    }
