'''
The main root file for the specified gRPC account server
'''

import os
import grpc

from concurrent import futures

from src.backend_services.account.database.database import database_initialization, Base, engine
from src.backend_services.account.authentication.login import UserAuthentication_Service
from src.backend_services.common.proto import user_login_pb2_grpc


def add_services(server: grpc.Server) -> None:
    '''
    All the services to be added to the gRPC server on startup.

    server (grpc.Server): the server to add the services to

    return (None):
    '''

    user_login_pb2_grpc.add_UserAuthServiceServicer_to_server(UserAuthentication_Service(), server)
    print('Service Added: User-Authentication')


def serve() -> None:
    '''
    Method to startup and initialise the gRPC server

    return (None):
    '''

    host = os.environ.get('ACCOUNT_HOST')
    port = os.environ.get('ACCOUNT_PORT')
    max_workers = int(os.environ.get('ACCOUNT_MAX_WORKERS'))

    print(f'Port: {port}')
    print(f'Max Workers Assigned: {max_workers}')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))

    server_credentials = grpc.ssl_server_credentials(
        [(open(os.environ.get('ACCOUNT_PKEY'), 'rb').read(), open(os.environ.get('ACCOUNT_CERT'), 'rb').read())]
    )

    server.add_secure_port(f'[::]:{port}', server_credentials)
    print(f'Starting gRPC server on https://{host}:{port}')
    server.start()

    database_initialization()
    Base.metadata.create_all(engine)

    add_services(server)

    print('Server Running')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
