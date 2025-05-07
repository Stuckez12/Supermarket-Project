import grpc

from src.backend_services.common.proto.input_output_messages_pb2 import HTTP_Response
from src.backend_services.common.proto import user_login_pb2, user_login_pb2_grpc
from src.backend_services.common.utils.data_verification import DataVerification
from src.backend_services.common.utils.schema import load_yaml_file_as_dict, insert_data_into_schema, format_schema_data_types


# Global file variables
REGISTRATION_VERIFY_CONFIG = None
LOGIN_VERIFY_CONFIG = None



def initialise_file():
    global REGISTRATION_VERIFY_CONFIG
    global LOGIN_VERIFY_CONFIG

    schemas = load_yaml_file_as_dict("src/backend_services/account/verification_config/registration.yaml")

    REGISTRATION_VERIFY_CONFIG = schemas['registration']
    LOGIN_VERIFY_CONFIG = None

initialise_file()


class UserAuthentication_Service(user_login_pb2_grpc.UserAuthService):
    '''
    This class holds all the grpc requests on the server side
    in regards to user login and authentication.
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

        data = {
            'email': request.email,
            'password': request.password,
            'first_name': request.first_name,
            'last_name': request.last_name,
            'gender': request.gender,
            'date_of_birth': request.date_of_birth,
        }

        schema = insert_data_into_schema(REGISTRATION_VERIFY_CONFIG, data)
        schema = format_schema_data_types(schema, to_string=False)

        verify = DataVerification()
        success, errors = verify.verify_data(schema)

        if not success:
            return_status.success = False
            return_status.http_status = 400
            return_status.message = 'Invalid Data Recieved'
            return_status.error.extend(errors)

            return user_login_pb2.UserRegistrationResponse(status=return_status)

        

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
