import input_output_messages_pb2 as _input_output_messages_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserRegistrationRequest(_message.Message):
    __slots__ = ("email", "password", "first_name", "last_name", "gender", "date_of_birth")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_BIRTH_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., gender: _Optional[str] = ..., date_of_birth: _Optional[str] = ...) -> None: ...

class UserData(_message.Message):
    __slots__ = ("uuid", "email", "password_last_changed_at", "first_name", "last_name", "gender", "date_of_birth", "created_at", "updated_at", "last_login", "email_verified", "user_status", "user_role")
    UUID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_LAST_CHANGED_AT_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_BIRTH_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_FIELD_NUMBER: _ClassVar[int]
    EMAIL_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    USER_STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_ROLE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    email: str
    password_last_changed_at: str
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    created_at: str
    updated_at: str
    last_login: str
    email_verified: bool
    user_status: str
    user_role: str
    def __init__(self, uuid: _Optional[str] = ..., email: _Optional[str] = ..., password_last_changed_at: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., gender: _Optional[str] = ..., date_of_birth: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., last_login: _Optional[str] = ..., email_verified: bool = ..., user_status: _Optional[str] = ..., user_role: _Optional[str] = ...) -> None: ...

class UserRegistrationResponse(_message.Message):
    __slots__ = ("status", "user")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    status: _input_output_messages_pb2.HTTP_Response
    user: UserData
    def __init__(self, status: _Optional[_Union[_input_output_messages_pb2.HTTP_Response, _Mapping]] = ..., user: _Optional[_Union[UserData, _Mapping]] = ...) -> None: ...

class UserLoginRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class UserLoginResponse(_message.Message):
    __slots__ = ("status", "user", "session", "otp_required")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    OTP_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    status: _input_output_messages_pb2.HTTP_Response
    user: UserData
    session: UserSession
    otp_required: bool
    def __init__(self, status: _Optional[_Union[_input_output_messages_pb2.HTTP_Response, _Mapping]] = ..., user: _Optional[_Union[UserData, _Mapping]] = ..., session: _Optional[_Union[UserSession, _Mapping]] = ..., otp_required: bool = ...) -> None: ...

class UserLogoutRequest(_message.Message):
    __slots__ = ("session_uuid", "user_uuid")
    SESSION_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    session_uuid: str
    user_uuid: str
    def __init__(self, session_uuid: _Optional[str] = ..., user_uuid: _Optional[str] = ...) -> None: ...

class OTPRequest(_message.Message):
    __slots__ = ("email", "otp_code")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    OTP_CODE_FIELD_NUMBER: _ClassVar[int]
    email: str
    otp_code: int
    def __init__(self, email: _Optional[str] = ..., otp_code: _Optional[int] = ...) -> None: ...

class UserSession(_message.Message):
    __slots__ = ("session_uuid", "expiry_time")
    SESSION_UUID_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_TIME_FIELD_NUMBER: _ClassVar[int]
    session_uuid: str
    expiry_time: int
    def __init__(self, session_uuid: _Optional[str] = ..., expiry_time: _Optional[int] = ...) -> None: ...
