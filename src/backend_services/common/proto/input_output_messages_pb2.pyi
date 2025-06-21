from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HTTP_Response(_message.Message):
    __slots__ = ("success", "http_status", "message", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    HTTP_STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    http_status: int
    message: str
    error: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, success: bool = ..., http_status: _Optional[int] = ..., message: _Optional[str] = ..., error: _Optional[_Iterable[str]] = ...) -> None: ...

class OTP_Response(_message.Message):
    __slots__ = ("status", "otp_required")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OTP_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    status: HTTP_Response
    otp_required: bool
    def __init__(self, status: _Optional[_Union[HTTP_Response, _Mapping]] = ..., otp_required: bool = ...) -> None: ...
