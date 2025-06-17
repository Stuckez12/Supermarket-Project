'''

'''

from google.protobuf.message import Message


def get_status_response_data(data: Message, embedded: bool=True) -> dict:
    '''
    Converts HTTP gRPC response messages into a dict ready to send to the client

    data (Message): google gRPC response message
    embedded (bool): whether the message is embedded or standalone [default - True]

    return (dict): formatted data in a dict
    '''

    if embedded:
        return {
            'success': data.status.success,
            'http_status': data.status.http_status,
            'message': data.status.message,
            'error': list(data.status.error)
        }

    return {
        'success': data.success,
        'http_status': data.http_status,
        'message': data.message,
        'error': list(data.error)
    }


def get_user_response_data(data: Message) -> dict:
    '''
    Converts user gRPC response messages into a dict ready to send to the client

    data (Message): google gRPC response message

    return (dict): formatted data in a dict
    '''

    return {
        'uuid': data.user.uuid,
        'email': data.user.email,
        'password_last_changed_at': data.user.password_last_changed_at,
        'first_name': data.user.first_name,
        'last_name': data.user.last_name,
        'gender': data.user.gender,
        'date_of_birth': data.user.date_of_birth,
        'created_at': data.user.created_at,
        'updated_at': data.user.updated_at,
        'last_login': data.user.last_login,
        'email_verified': data.user.email_verified,
        'user_status': data.user.user_status,
        'user_role': data.user.user_role
    }


def get_session_response_data(data: Message) -> dict:
    '''
    Converts session gRPC response messages into a dict ready to send to the client

    data (Message): google gRPC response message

    return (dict): formatted data in a dict
    '''

    return {
        'session_uuid': data.session.session_uuid,
        'expiry_time': data.session.expiry_time
    }
