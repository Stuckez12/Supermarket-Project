import grpc

from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response
from src.backend_services.common.proto import user_login_pb2, user_login_pb2_grpc


class UserAuthentication_Service(user_login_pb2_grpc.UserAuthService):
    '''
    This class holds all the grpc requests on the server side and returns the relevant data.
    '''


    def UserRegistration(self, request: user_login_pb2.UserRegistrationRequest, context: grpc.ServicerContext) -> user_login_pb2.UserRegistrationResponse:
        '''
        This gRPC function recieves registration details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.
        '''
        
        print("UserRegistration Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )
        
        return user_login_pb2.UserRegistrationResponse(status=return_status)


    def UserLogin(self, request: user_login_pb2.UserLoginRequest, context: grpc.ServicerContext) -> user_login_pb2.UserLoginResponse:
        '''
        This gRPC function recieves login details from the request.
        The data recieved is validated and inserted into the database.
        If any errors arise then relevant error messages are returned.
        '''
        
        print("UserLogin Request Made:")
        print(request)

        return_status = HTTP_Response(
            success=True,
            http_status=200,
            message='Request Successful'
        )
        
        return user_login_pb2.UserLoginResponse(status=return_status)
