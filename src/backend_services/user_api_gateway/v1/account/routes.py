from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from src.backend_services.common.proto import user_login_pb2
from src.backend_services.common.proto.user_login_pb2_grpc import UserAuthServiceStub


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


def get_grpc_client(request: Request):
    client = request.app.state.account_grpc_client
    client.reconnect()
    return client


@router.post("/register")
async def register_user(request_data: RegisterRequest, client = Depends(get_grpc_client)):

    print(request_data.email)
    print(request_data.password)
    print(request_data.first_name)
    print(request_data.last_name)
    print(request_data.date_of_birth)
    print(request_data.gender)

    data = user_login_pb2.UserRegistrationRequest(
        email=request_data.email,
        password=request_data.password,
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        date_of_birth=request_data.date_of_birth,
        gender=request_data.gender
    )

    success, data = client.grpc_request('UserRegistration', data)

    new_data = {
        'success': data.success,
        'http_status': data.http_status,
        'message': data.message
    }

    return [{"success": success, 'data': new_data}]


@router.post("/login")
async def login_user():
    return [{"id": 1, "name": "John"}]


@router.post("/verification/otp/email")
async def otp_verification():
    return [{"id": 1, "name": "John"}]


@router.post("/logout")
async def logout_user():
    return [{"id": 1, "name": "John"}]