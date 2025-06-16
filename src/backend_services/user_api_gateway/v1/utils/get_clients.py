'''
File containing all functions to get every type of
ServerCommunication class that has been setup for FastAPI servers
'''

from fastapi import Request

from src.backend_services.common.gRPC.server_connection import ServerCommunication


def get_grpc_account_client(request: Request) -> ServerCommunication:
    '''
    Fetches initialised ServerCommunication stored in a FastAPI server.

    request (Request): the request object used by FastAPI to access incomming HTTP requests

    return (ServerCommunication): returns an initialised class that communicates with the account service
    '''

    client = request.app.state.account_grpc_client
    client.reconnect()
    return client
