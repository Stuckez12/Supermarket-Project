'''
This file holds a class that is used to communicate to different gRPC servers.
'''

import grpc
import random
import time

from google.protobuf.message import Message
from typing import Callable, Self, Tuple, TypeVar, Union

from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response


STUB = TypeVar("gRPC Stubs")


DEFAULT_CHANNEL_OPTIONS = [
    # Defines the maximum data size of data one RPC 
    # call can send to a server.
    # Data is in bytes (default - 10MB)
    ('grpc.max_send_message_length', 10000000),
    # Defines the maximum data size of data one RPC
    # call can recieve from a response.
    # Data is in bytes (default - 10MB)
    ('grpc.max_receive_message_length', 10000000),
    # Defines how long the connection lasts between
    # the two servers before disconnecting (saves resources).
    # Time is in milliseconds (default - 60 seconds)
    ('grpc.max_connection_idle_ms', 60000),
    # Whether to allow keepalive pings when
    # there are no active RPC calls.
    # (default - 1 (True))
    ('grpc.keepalive_permit_without_calls', 1),
    # Periodically pings the server every interval
    # keeping the connection alive
    # Time is in milliseconds (default - 5 seconds)
    ('grpc.keepalive_time_ms', 5000),
    # Forces the client to wait x time until sending another
    # ping top the connected server.
    # This prevents the client from sending ping more
    # frequently than needed.
    # Time is in milliseconds (default - 5 seconds)
    ('grpc.http2.min_time_between_pings_ms', 5000),
    # How long to wait for a response from the last ping.
    # If no response then the connection is terminated.
    # Time is in milliseconds (default - 2 seconds)
    ('grpc.keepalive_timeout_ms', 2000),
    # Defines how many consecutive pings to send before
    # adding a strike to the connection.
    # This only happens when there has been
    # no RPC calls that return data.
    # (default - 12 inactive pings before a strike)
    ('grpc.http2.max_pings_without_data', 12),
    # Defines how many strikes are allowed to accumulate
    # before terminating the connection.
    # Strikes are permanent until termination and reconnection.
    # (default - 3 strikes)
    ('grpc.http2.max_ping_strikes', 3),
    # Defines the initial backoff time before attempting to reconnect.
    # Time is in milliseconds (default - 0.5 seconds)
    ('grpc.initial_reconnect_backoff_ms', 500),
    # Defines the minimum time between reconnection attempts.
    # Time is in milliseconds (default - 0.5 seconds)
    ('grpc.min_reconnect_backoff_ms', 500),
    # Defines the maximum time between reconnection attempts.
    # Each failed attempt doubles the backoff time until it
    # reaches the specified time below.
    # Time is in milliseconds (default - 4 seconds)
    ('grpc.max_reconnect_backoff_ms', 4000)
]


class ServerCommunication():
    '''
    This class is used to communicate to a gRPC server and
    receive the desired results from the data given with
    the specified request made. It creates a channel to the
    specified server (secure or insecure) and retries sending
    the request until either a successful response was given
    or the max ammount of attempts were used.

    When a failed response is received, depending on the error,
    it reconnects to the server which ensures that the
    connection was not the issue. This class should only be
    initialised once on startup and then called upon by the
    running server when it is needed.
    '''

    host = None
    port = None
    secure_channel = False
    options = []

    channel = None

    def __init__(
            cls: Self,
            channel_host: str,
            channel_port: str,
            channel_secure: bool=False,
            server_certificate: str=None,
            rpc_max_retries: int=3,
            channel_options: list=DEFAULT_CHANNEL_OPTIONS
        ) -> None:

        '''
        Initialising the class by receiving all the variables required
        to create and send a request to the targeted gRPC server.

        cls (Self): the ServerCommunication class
        channel_host (str): the host used to call the server
        channel_port (str): what port the server is located on within the host
        channel_secure (bool): whethewr to use a secure channel or an insecure channel [default - False]
        server_certificate (str): the root to the servers certificate [default - None]
        rpc_max_retries (int): how many times should the request be attempted [default - 3]
        channel_options (list): a list of gRPC channel options [default - DEFAULT_CHANNEL_OPTIONS]

        return (None): Nothing is returned
        '''

        cls.host = channel_host
        cls.port = channel_port

        cls.stub = None

        cls.secure_channel = channel_secure
        cls.certificate = None

        cls.options = channel_options
        cls.max_retries = rpc_max_retries

        if cls.secure_channel:
            if server_certificate is None:
                error_msg = f'Failed To Initialise ServerCommunication For {cls.host}:{cls.port}. Server Certificate Must Be Provided'
                raise AttributeError(error_msg)

            else:
                credentials = open(server_certificate, 'rb').read()
                cls.certificate = grpc.ssl_channel_credentials(root_certificates=credentials)

        cls.reconnect()


    def reconnect(cls: Self) -> None:
        '''
        Attempts to connect to the specified server using
        either a secure channel or insecure channel.
        Once connected, it then initialises a gRPC stub.

        cls (Self): the ServerCommunication class

        return (None): Nothing is returned
        '''

        url = cls.host + ':' + cls.port

        if cls.secure_channel:
            cls.channel = grpc.secure_channel(url, cls.certificate, options=cls.options)

        else:
            cls.channel = grpc.insecure_channel(url, options=cls.options)


    def grpc_request(
            cls: Self,
            request: Union[str, Callable],
            stub: Callable[[], STUB],
            data: Message
        ) -> Tuple[bool, Union[Message, HTTP_Response]]:

        '''
        With the provided method and data, it sends one request
        to the dedicated server and receives a single response.
        Depending on the result of the request, the function either
        returns a successful response from the server or retries
        the request.

        However if unable to or too many retries have been attempted,
        the function returns a false response with an HTTP_Response
        error in regards to the last erroneous gRPC call.

        cls (Self): the ServerCommunication class
        stub (Callable): a gRPC stub class that has yet to be executed
        request (str, Callable):
            the request is the function to call the gRPC server.
            it can either be a string or the actual calling method.
        data (Message): the proto data structure containing the message request data

        return (bool, [Message, HTTP_Response]): Nothing is returned
        '''

        retryable_errors = [
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.INTERNAL,
            grpc.StatusCode.DEADLINE_EXCEEDED
        ]

        backoff_factor = 0.5

        for attempt in range(cls.max_retries):
            try:
                stub_channel = stub(cls.channel)
                
                if isinstance(request, str):
                    call_func = getattr(stub_channel, request)

                else:
                    call_func = request

                return True, call_func(data)

            except grpc.RpcError as e:
                status_code = e.code()

                # The server either currently unavailable, crashed or took too long to respons
                if status_code in retryable_errors:
                    if attempt < cls.max_retries - 1:
                        sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                        time.sleep(sleep_time)
                        cls.reconnect()

                    else:
                        if status_code == grpc.StatusCode.UNAVAILABLE:
                            return False, HTTP_Response(
                                success=False,
                                http_status=500,
                                message='Either Certificate Config Error Or Service Unreachable'
                            )

                        elif status_code == grpc.StatusCode.INTERNAL:
                            return False, HTTP_Response(
                                success=False,
                                http_status=500,
                                message='Internal Server Error'
                            )

                        elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                            return False, HTTP_Response(
                                success=False,
                                http_status=500,
                                message='Server Took Too Long To Respond'
                            )

                # Response is missing authentication headers or invalid certificates
                elif status_code == grpc.StatusCode.UNAUTHENTICATED:
                    return False, HTTP_Response(
                        success=False,
                        http_status=500,
                        message='Either Client Certificate Missing Or Server Certificate Invalid'
                    )

                # Requests Data Is Malformed And Invalid
                elif status_code == grpc.StatusCode.INVALID_ARGUMENT:
                    return False, HTTP_Response(
                        success=False,
                        http_status=400,
                        message='The Provided Input Is Incorrectly Formatted'
                    )

                # RPC Request Does Not Exist
                elif status_code == grpc.StatusCode.UNIMPLEMENTED:
                    return False, HTTP_Response(
                        success=False,
                        http_status=501,
                        message='RPC Call Does Not Exist Or Is Currently Not Implemented'
                    )

                # Too Much Data Was Being Sent Over. Exceeds Data Limit Setting
                elif status_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
                    return False, HTTP_Response(
                        success=False,
                        http_status=400,
                        message='Maximum Data Provided Exceeds Data Limit'
                    )

            except AttributeError:
                return False, HTTP_Response(
                    success=False,
                    http_status=500,
                    message='Provided RPC Function Does Not Exist Or Stub Not Initialised'
                )

            except TypeError:
                return False, HTTP_Response(
                    success=False,
                    http_status=500,
                    message='Provided Request Is Not Callable Or A String'
                )

            except Exception:
                return False, HTTP_Response(
                    success=False,
                    http_status=500,
                    message='An Unexpected Error Occured'
                )
            
        return False, HTTP_Response(
            success=False,
            http_status=500,
            message='No Response Received'
        )
