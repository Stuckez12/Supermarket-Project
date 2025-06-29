'''
This file holds all the unique ServerCommunication
instances that communicate to all gRPC servers.
If any service wants to send a message to a gRPC service,
they must fetch the clients initialised in this file and
save the object in their internal server.
'''

import os

from src.backend_services.common.gRPC.server_connection import ServerCommunication


account_client = ServerCommunication(
    os.environ.get('ACCOUNT_SERVICE_NAME'),
    os.environ.get('ACCOUNT_PORT'),
    channel_secure=True,
    server_certificate=os.environ.get('ACCOUNT_CERT'),
    rpc_max_retries=1
)
