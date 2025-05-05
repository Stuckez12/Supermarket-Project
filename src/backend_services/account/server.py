import os
import grpc
from concurrent import futures

from src.backend_services.account.database.database import engine, Base, database_initialization

os.environ["GRPC_DNS_RESOLVER"] = "native"


def serve():
    port = os.environ.get('ACCOUNT_PORT')
    max_workers = int(os.environ.get('ACCOUNT_MAX_WORKERS'))

    print(f'Port: {port}')
    print(f'Max Workers Assigned: {max_workers}')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    server.add_insecure_port('[::]:' + port)
    server.start()

    database_initialization()
    Base.metadata.create_all(engine)

    server.wait_for_termination()

if __name__ == '__main__':
    serve()
