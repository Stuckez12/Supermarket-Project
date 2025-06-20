import input_output_messages_pb2 as _input_output_messages_pb2
import user_login_pb2 as _user_login_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBasicAccountDetailsRequest(_message.Message):
    __slots__ = ("user_uuid",)
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ...) -> None: ...

class BasicAccountDetailsResponse(_message.Message):
    __slots__ = ("status", "user")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    status: _input_output_messages_pb2.HTTP_Response
    user: _user_login_pb2.UserData
    def __init__(self, status: _Optional[_Union[_input_output_messages_pb2.HTTP_Response, _Mapping]] = ..., user: _Optional[_Union[_user_login_pb2.UserData, _Mapping]] = ...) -> None: ...

class UpdateUserEmailRequest(_message.Message):
    __slots__ = ("session_uuid", "user_uuid", "current_email", "new_email")
    SESSION_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    NEW_EMAIL_FIELD_NUMBER: _ClassVar[int]
    session_uuid: str
    user_uuid: str
    current_email: str
    new_email: str
    def __init__(self, session_uuid: _Optional[str] = ..., user_uuid: _Optional[str] = ..., current_email: _Optional[str] = ..., new_email: _Optional[str] = ...) -> None: ...

class UpdateUserPasswordRequest(_message.Message):
    __slots__ = ("user_uuid", "email", "current_password", "new_password")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    email: str
    current_password: str
    new_password: str
    def __init__(self, user_uuid: _Optional[str] = ..., email: _Optional[str] = ..., current_password: _Optional[str] = ..., new_password: _Optional[str] = ...) -> None: ...

class UpdateUserDetailsRequest(_message.Message):
    __slots__ = ("user_uuid", "first_name", "last_name", "gender", "date_of_birth")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_BIRTH_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    def __init__(self, user_uuid: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., gender: _Optional[str] = ..., date_of_birth: _Optional[str] = ...) -> None: ...

class DeleteAccountRequest(_message.Message):
    __slots__ = ("user_uuid", "email")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    email: str
    def __init__(self, user_uuid: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...
