import sys
sys.path.insert(0, 'C:\\Users\\jakes\\Documents\\GitHub\\Personal\\Supermarket-Project')





import grpc
from src.backend_services.common.proto.user_login_pb2_grpc import UserAuthServiceStub


url = 'localhost:50051'

credentials = open('..certificates.account.account-cert.pem', 'rb').read()
certificate = grpc.ssl_channel_credentials(root_certificates=credentials)


channel = grpc.secure_channel(url, credentials=certificate)


stubbing = UserAuthServiceStub