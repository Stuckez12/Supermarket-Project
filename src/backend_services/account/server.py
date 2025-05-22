import os
import grpc

from concurrent import futures

from src.backend_services.account.database.database import Base, engine, database_initialization
from src.backend_services.account.authentication.login import UserAuthentication_Service
from src.backend_services.common.proto import user_login_pb2_grpc


os.environ["GRPC_DNS_RESOLVER"] = "native"


def add_services(server):
    user_login_pb2_grpc.add_UserAuthServiceServicer_to_server(UserAuthentication_Service(), server)
    print('Service Added: User-Authentication')


def serve():
    port = os.environ.get('ACCOUNT_PORT')
    max_workers = int(os.environ.get('ACCOUNT_MAX_WORKERS'))

    print(f'Port: {port}')
    print(f'Max Workers Assigned: {max_workers}')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))

    server_credentials = grpc.ssl_server_credentials(
        [(open('localhost-key.pem', 'rb').read(), open('localhost-cert.pem', 'rb').read())]
    )

    server.add_secure_port(f'[::]:{port}', server_credentials)
    print(f'Starting gRPC server on https://localhost:{port}')
    server.start()

    database_initialization()
    Base.metadata.create_all(engine)

    add_services(server)

    print('Server Running')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
