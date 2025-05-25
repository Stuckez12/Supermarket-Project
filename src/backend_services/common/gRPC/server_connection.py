'''

'''

import grpc
import random
import time

from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response


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
    
    '''

    host = None
    port = None
    secure_channel = False
    options = []

    channel = None
    stub = None

    def __init__(cls, channel_host, channel_port, grpc_stub, channel_secure=False, rpc_max_retries=3, channel_options=DEFAULT_CHANNEL_OPTIONS):
        '''
        
        '''

        cls.host = channel_host
        cls.port = channel_port
        cls.secure_channel = channel_secure
        cls.options = channel_options
        cls.stub = grpc_stub
        cls.max_retries = rpc_max_retries

        cls.reconnect()


    def reconnect(cls):
        '''
        
        '''

        url = cls.host + ':' + cls.port

        cls.channel = grpc.secure_channel(url, options=cls.options) if cls.secure_channel else grpc.insecure_channel(url, options=cls.options)
        cls.stub = cls.stub(cls.channel)


    def grpc_request(cls, request, data):
        '''
        
        '''

        retryable_errors = [
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.INTERNAL,
            grpc.StatusCode.DEADLINE_EXCEEDED
        ]

        backoff_factor = 0.5

        for attempt in range(cls.max_retries):
            try:
                if isinstance(request, str):
                    call_func = getattr(cls.stub, request)
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
                                message='Either Client Certificate Missing Or Server Certificate Invalid'
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
