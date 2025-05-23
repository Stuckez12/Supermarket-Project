'''

'''

from src.backend_services.common.proto import user_login_pb2


def user_proto_format(user):
    '''
    
    '''

    return user_login_pb2.UserData(
        uuid=user.uuid,
        email=user.email,
        password_last_changed_at=int(user.password_last_changed_at.timestamp()),
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        date_of_birth=str(user.date_of_birth),
        created_at=int(user.created_at.timestamp()),
        updated_at=int(user.updated_at.timestamp()),
        last_login=int(user.last_login.timestamp()),
        email_verified=user.email_verified,
        user_status=user.user_status,
        user_role=user.user_role,
    )
