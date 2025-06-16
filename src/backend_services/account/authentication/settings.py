'''
This file holds the generic authentication for a user on the gRPC account-service
'''

import grpc
import json
import os
import uuid

from typing import Self

from src.backend_services.common.proto import user_actions_pb2, user_actions_pb2_grpc
from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response, OTP_Response



class UserAction_Service(user_actions_pb2_grpc.UserSettingsService):
    '''
    This class holds all the gRPC requests on the server side
    in regards to user login and authentication.
    '''


    def GetBasicAccountData(cls: Self, request: user_actions_pb2.GetBasicAccountDetailsRequest, context: grpc.ServicerContext) -> user_actions_pb2.BasicAccountDetailsResponse:
        '''
        This gRPC function recieves a user uuid from the request.
        The data recieved is validated and data related to the user and return the users' data.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (GetBasicAccountDetailsRequest): the specified proto defined request message for the rpc call

        return (BasicAccountDetailsResponse): the proto Message response including user data and request status
        '''

        print("GetBasicAccountData Request Made:")
        print(request)

        return None


    def UpdateUserEmail(cls: Self, request: user_actions_pb2.UpdateUserEmailRequest, context: grpc.ServicerContext) -> OTP_Response:
        '''
        This gRPC function recieves a user uuid and the new email from the request.
        The data recieved is validated and the data is updated on the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (UpdateUserEmailRequest): the specified proto defined request message for the rpc call

        return (OTP_Response): the proto Message response with the request status
        '''

        print("UpdateUserEmail Request Made:")
        print(request)

        return None


    def UpdateUserPassword(cls: Self, request: user_actions_pb2.UpdateUserPasswordRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves a user uuid and the new password from the request.
        The data recieved is validated and the data is updated on the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (UpdateUserPasswordRequest): the specified proto defined request message for the rpc call

        return (HTTP_Response): the proto Message response with the request status
        '''

        print("UpdateUserPassword Request Made:")
        print(request)

        return None


    def UpdateUserDetails(cls: Self, request: user_actions_pb2.UpdateUserDetailsRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves a user uuid from the request.
        The data recieved is validated and data related to the user and return the users' data.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (UpdateUserDetailsRequest): the specified proto defined request message for the rpc call

        return (HTTP_Response): the proto Message response including user data and request status
        '''

        print("UpdateUserDetails Request Made:")
        print(request)

        return None


    def DeleteAccount(cls: Self, request: user_actions_pb2.DeleteAccountRequest, context: grpc.ServicerContext) -> HTTP_Response:
        '''
        This gRPC function recieves a user uuid and email from the request.
        The data recieved is validated and deletes the users' data from the database.
        If any errors arise then relevant error messages are returned.

        cls (Self): the UserAction_Service class
        request (DeleteAccountRequest): the specified proto defined request message for the rpc call

        return (HTTP_Response): the proto Message response including user data and request status
        '''

        print("DeleteAccount Request Made:")
        print(request)

        return None
