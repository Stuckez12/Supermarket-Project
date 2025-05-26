from fastapi import Request


def get_grpc_account_client(request: Request):
    client = request.app.state.account_grpc_client
    client.reconnect()
    return client
