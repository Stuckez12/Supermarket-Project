'''
This file holds all the common utility functions that are currently uncategorised.
'''

from src.backend_services.account.database.models import User
from src.backend_services.common.proto.user_login_pb2 import UserData


def user_proto_format(user: User) -> UserData:
    '''
    This function takes the entire object row of the searched
    user and filters the data to only include publically accessible
    information. Once filtered down it inserts the data into a
    proto message ready to be sent to the client.

    user (User): the sqlalchemy user object containing one user

    return (UserData): filtered down data of the relevant user
    '''

    return UserData(
        uuid=user.uuid,
        email=user.email,
        password_last_changed_at=user.password_last_changed_at,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        date_of_birth=str(user.date_of_birth),
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        email_verified=user.email_verified,
        user_status=user.user_status,
        user_role=user.user_role,
    )
