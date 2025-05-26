'''

'''

import os

from functools import partial

from src.backend_services.common.gRPC.server_connection import ServerCommunication

from src.backend_services.common.proto.user_login_pb2_grpc import UserAuthServiceStub

account_client = ServerCommunication(
    os.environ.get('ACCOUNT_SERVICE_NAME'),
    os.environ.get('ACCOUNT_PORT'),
    partial(UserAuthServiceStub),
    channel_secure=True,
    server_certificate=os.environ.get('ACCOUNT_CERT'),
    rpc_max_retries=1
)
