'''
File containing a class to validate all types of data.
'''

import dns.resolver
import uuid

from datetime import datetime, timezone
from enum import Enum
from math import inf as INFINITY
from typing import Any, Callable, Self, Tuple, TypeVar

ENUM_CLASS = TypeVar('Enum Class', bound=Enum)


# May be moved to seperate file
class CharReqEnum(Enum):
    MUST = 'MUST'
    DEFAULT = 'DEFAULT'
    NONE = 'NONE'


    @classmethod
    def from_name(cls: Self, name: str):
        return cls.members.get(name.upper())


    @classmethod
    def from_value(cls: Self, value: Any):
        for member in cls:
            if member.value == value:
                return member

        return None
    

# May be moved to seperate file
class UnixNumberFormatEnum(Enum):
    SECONDS = 'SECONDS'
    MINUTES = 'MINUTES'
    HOURS = 'HOURS'
    DAYS = 'DAYS'
    YEARS = 'YEARS'


    @classmethod
    def from_name(cls: Self, name: str):
        return cls.members.get(name.upper())


    @classmethod
    def from_value(cls: Self, value: Any):
        for member in cls:
            if member.value == value:
                return member

        return None
    

# May be moved to seperate file
class NullBooleanEnum(Enum):
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NONE = 'NONE'


    @classmethod
    def from_name(cls: Self, name: str):
        return cls.members.get(name.upper())


    @classmethod
    def from_value(cls: Self, value: Any):
        for member in cls:
            if member.value == value:
                return member

        return None


class DataVerification():
    '''
    This class contains all the functions that are
    used to check and validate specific data.
    It is highly customisable with the restrictions
    dictionary that you can apply to each verification
    function. However, each function takes different
    restriction inputs that depend on the data type.
    '''


    def set_min_restriction(cls: Self, default_value: int, restrictions: dict) -> int:
        '''
        This function sets the minimum size a number can be.

        cls (Self): the verification class
        default_value (int): the default value to set the restriction to
        restrictions (dict): the restrictions set on the data

        return (int, list): the new restricted number
        '''

        if 'min_num' in restrictions:
            return restrictions['min_num']

        elif 'min_len' in restrictions:
            return restrictions['min_len']

        return default_value


    def set_max_restriction(cls: Self, default_value: int, restrictions: dict) -> int:
        '''
        This function sets the maximum size a number can be.

        cls (Self): the verification class
        default_value (int): the default value to set the restriction to
        restrictions (dict): the restrictions set on the data

        return (int, list): the new restricted number
        '''

        if 'max_num' in restrictions:
            return restrictions['max_num']

        elif 'max_len' in restrictions:
            return restrictions['max_len']

        return default_value


    def set_data_type_restriction(
            cls: Self,
            name: str,
            restrictions: dict,
            limit_to: list[type],
            rest_errors: list
        ) -> Tuple[type, list]:

        '''
        This function sets the variable in the restrictions
        to the desired data type to check against.
        If it is unable to find the desired data type, it defaults
        to the first data type that is provided to the function.

        cls (Self): the verification class
        name (str): the name of the variable
        restrictions (dict): the restrictions set on the data
        limit_to (list[type]): how to treat the variable. e.g. for a number either int or float
        rest_errors (list): the list of accumulated errors

        return (type, list): the type to treat the data as and the errors
        '''

        if 'type' in restrictions:
            if restrictions['type'] in limit_to:
                return restrictions['type'], rest_errors

            else:
                rest_errors.append(f'DEV ERROR: {name}-restriction-type is invalid. Data type must be within specified limit {limit_to}')

        return limit_to[0], rest_errors

        
    def set_enum_restriction(
            cls: Self,
            name: str,
            ClassEnum: ENUM_CLASS,
            restrictions: dict,
            value: str,
            rest_errors: list
        ) -> Tuple[ENUM_CLASS, list]:

        '''
        This function converts an ENUM string to the class representation.
        If the specified value is not present in the restrictions, it
        assigns the output to the DEFAULT class value.

        cls (Self): the verification class
        name (str): the name of the variable
        ClassEnum (ENUM_CLASS): a class holding custom enum values
        restrictions (dict): the restrictions set on the data
        value (str): the specified restriction
        rest_errors (list): the total errors

        return (ENUM_CLASS, list): the class based enum data and errors
        '''

        if value in restrictions:
            new_val = ClassEnum.from_value(restrictions[value])

            if new_val is None:
                rest_errors.append(f'DEV ERROR: {name}-restriction-{value} is invalid. {value} must be a value within CharReqEnum')

            return new_val, rest_errors

        return ClassEnum.DEFAULT, rest_errors


    def validate_char_requirement(
            cls: Self,
            data: str,
            char_check_fn: Callable,
            requirement: ENUM_CLASS,
            name: str,
            char_req: str,
            data_errors: list
        ) -> list:

        '''
        This function checks whether the characters (specified
        by the provided function) are present within a string.
        It uses the CharReqEnum state to check whether the characters
        should be present in the string or not included.

        cls (Self): the verification class
        data (str): the data to check
        char_check_fn (Callable): the function to use to check character requirements
        requirement (ENUM_CLASS): a specified class state. The class holds custom enum values
        name (str): the name of the variable
        char_req (str): the name of the requirement
        data_errors (list): the total errors

        return (list): the errors when applying restrictions
        '''

        if requirement == CharReqEnum.DEFAULT:
            return data_errors

        has_char = any(char_check_fn(char) for char in data)

        if has_char and requirement == CharReqEnum.NONE:
            data_errors.append(f'{name} must not contain {char_req}')

        elif not has_char and requirement == CharReqEnum.MUST:
            data_errors.append(f'{name} must contain at least one {char_req}')

        return data_errors


    def verify_data(cls: Self, data: dict) -> Tuple[bool, list]:
        '''
        This function recieves nested dictionaries containing the
        variables and the expected data type and restrictions for
        each variable.

        Example string input: -

        data = {
            variable_name: {
                type: str,
                data: "hello",
                check: True,
                restrictions: {
                    min_len: 4,
                    max_len: 8,
                    lower_case: "MUST",
                    upper_case: "MUST",
                    numbers: "DEFAULT",
                    symbols: "NONE"
                }
            },
            {
                # etc, etc, etc
            }
        }

        The dictionary will be looped through and call the relevant
        verification function depending on the type of data.
        The value of the variable is held in "data" and all the
        restrictions that are upheld for the variable is all organised
        in its respective dictionary. If the restriction is not defined
        then it will default to its origional value.

        cls (Self): the verification class
        data (dict): the data to check, including restrictions

        return (bool, list): a success flag and the errors detected are returned
        '''

        total_errors = []
        optional_errors = []

        for variable, data_points in data.items():
            if not data_points['check']:
                continue

            success = True
            errors = []

            data = data_points['data']
            restrictions = {}

            optional = False

            if 'optional' in data_points:
                if data_points['optional']:
                    optional = True

            if 'skip_empty' in data_points:
                if data_points['skip_empty']:
                    if data == '':
                        continue
 
            if 'restrictions' in data_points:
                restrictions = data_points['restrictions']

            # TODO: Rework to be a dictionary, making it more maintainable
            if data_points['type'] == str:
                success, errors = cls.verify_string_data(variable, data, restrictions)

            elif data_points['type'] in [int, float]:
                restrictions['type'] = data_points['type']
                success, errors = cls.verify_number_data(variable, data, restrictions)

            elif data_points['type'] == 'email':
                success, errors = cls.verify_email_data(variable, data)

            elif data_points['type'] == 'str_uuid':
                success, errors = cls.verify_uuid4_string(variable, data)

            elif data_points['type'] == 'unix':
                success, errors = cls.verify_unix(variable, data, restrictions)

            elif data_points['type'] == 'datetime':
                success, errors = cls.verify_datetime_string(variable, data, restrictions)

            if optional:
                optional_errors += errors

            else:
                if len(errors) != 0 and not success:
                    total_errors += errors

        if len(total_errors) != 0:
            return False, total_errors + optional_errors
        
        return True, optional_errors


    def verify_string_data(
            cls: Self,
            name: str,
            data: Any,
            restrictions: dict={}
        ) -> Tuple[bool, list]:

        '''
        With the relevant restrictions and data, this function will verify
        the specified data checking that it is a string and return the
        necessary errors if any.
        It is not mandatory to pass through all the restrictions that
        are enforced onto the string.
        You can pass through an empty restrictions dict which will then
        default all the restrictions to their standard parameters.

        Example Restriction: -

        restrictions = {
            min_len: 12,
            upper_case: "MUST",
            symbols: "MUST"
        }

        Available Restrictions:
        - **min_len (int)**:
            - DEFAULT = 0
            - Specifies the minimum length of the string. 
            - Must be smaller than `max_len` if `max_len` is also provided.

        - **max_len (int)**: 
            - DEFAULT = INFINITY
            - Specifies the maximum length of the string. 
            - Must be larger than `min_len` if `min_len` is also provided.

        - **lower_case (str)**: 
            - DEFAULT = "DEFAULT"
            - Accepts the `CharacterRequirementStatus` Enum.
            - Determines if lowercase letters are required in the string.

        - **upper_case (str)**: 
            - DEFAULT = "DEFAULT"
            - Accepts the `CharacterRequirementStatus` Enum.
            - Determines if uppercase letters are required in the string.

        - **numbers (str)**: 
            - DEFAULT = "DEFAULT"
            - Accepts the `CharacterRequirementStatus` Enum.
            - Determines if numbers are required in the string.

        - **symbols (str)**: 
            - DEFAULT = "DEFAULT"
            - Accepts the `CharacterRequirementStatus` Enum.
            - Determines if special symbols are required in the string.


        `CharacterRequirementStatus` Enum:
        - **MUST**: 
            - The presence of this data is **mandatory**. 
            - The string must contain this specific character type.

        - **DEFAULT**: 
            - The presence of this data is **optional**. 
            - The string may or may not contain this specific character type.

        - **NONE**: 
            - There must be **no presence** of this data.
            - The string must not contain this specific character type.

        cls (Self): the verification class
        name (str): the name of the data
        data (Any): the data to be verified
        restrictions (dict): a dictionary of all the restrictions to apply [default - {}]

        return (bool, list): returns a success flag and a list of errors detected
        '''

        if type(data) != str:
            return False, [f'{name} type is invalid. Expected str but received {type(data).__name__}']
        
        # Default Restrictions
        min_len = 0
        max_len = INFINITY
        lower_case = CharReqEnum.DEFAULT
        upper_case = CharReqEnum.DEFAULT
        numbers = CharReqEnum.DEFAULT
        symbols = CharReqEnum.DEFAULT

        rest_errors = []

        # Formatting Restrictions
        min_len = cls.set_min_restriction(min_len, restrictions)
        max_len = cls.set_max_restriction(max_len, restrictions)
        lower_case, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'lower_case', rest_errors)
        upper_case, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'upper_case', rest_errors)
        numbers, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'numbers', rest_errors)
        symbols, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'symbols', rest_errors)

        if max_len < min_len:
            rest_errors.append(f'DEV ERROR: {name}-restriction-len_limits is invalid. max_len must be >= min_len')

        if min_len < 0:
            rest_errors.append(f'DEV ERROR: {name}-restriction-min_len is invalid. min_len must be a positive integer')

        if len(rest_errors) != 0:
            return False, rest_errors
        
        data_errors = []

        # Checking data to specified restrictions
        data_len = len(data)

        if data_len < min_len:
            data_errors.append(f'{name} string length of {data_len} is too short. Minimum expected length is {min_len} characters')

        if data_len > max_len:
            data_errors.append(f'{name} string length of {data_len} is too long. Maximum expected length is {max_len} characters')

        data_errors = cls.validate_char_requirement(data, str.islower, lower_case, name, 'lower_case', data_errors)
        data_errors = cls.validate_char_requirement(data, str.isupper, upper_case, name, 'upper_case', data_errors)
        data_errors = cls.validate_char_requirement(data, str.isdigit, numbers,    name, 'number',     data_errors)
        data_errors = cls.validate_char_requirement(data, lambda c: not c.isalnum(), symbols,    name, 'symbol',     data_errors)

        if len(data_errors) != 0:
            return False, data_errors

        return True, []


    def verify_number_data(
            cls: Self,
            name: str,
            data: Any,
            restrictions: dict={}
        ) -> Tuple[bool, list]:

        '''
        With the relevant restrictions and data, this function will verify
        the specified data checking that it is a integer or float and
        return the necessary errors if any.
        It is not mandatory to pass through all the restrictions that
        are enforced onto the number.
        You can pass through an empty restrictions dict which will then
        default all the restrictions to their standard parameters.

        Example Restriction: -

        restrictions = {
            type: int
            max_num: 12,
        }

        Available Restrictions:
        - **type (type)**:
            - DEFAULT = int
            - Specifies whether the data must be an integer (int) or float (float).

        - **min_num (int)**:
            - DEFAULT = -INFINITY
            - Specifies the minimum size of the number. 
            - Must be smaller than `max_num` if `max_num` is also provided.

        - **max_num (int)**: 
            - DEFAULT = INFINITY
            - Specifies the maximum size of the number. 
            - Must be larger than `min_num` if `min_num` is also provided.

        cls (Self): the verification class
        name (str): the name of the data
        data (Any): the data to be verified
        restrictions (dict): a dictionary of all the restrictions to apply [default - {}]

        return (bool, list): returns a success flag and a list of errors detected
        '''

        # Default Restrictions
        min_num = -INFINITY
        max_num = INFINITY

        rest_errors = []

        # Formatting Restrictions
        data_type, rest_errors = cls.set_data_type_restriction(name, restrictions, [int, float], rest_errors)
        min_num = cls.set_min_restriction(min_num, restrictions)
        max_num = cls.set_max_restriction(max_num, restrictions)

        if data_type.__name__ == 'float':
            try:
                data = float(data)

            except:
                return False, [f'{name} type is invalid. Expected {data_type.__name__} but received {type(data).__name__}']

        if type(data).__name__ != data_type.__name__:
            return False, [f'{name} type is invalid. Expected {data_type.__name__} but received {type(data).__name__}']

        if max_num < min_num:
            rest_errors.append(f'DEV ERROR: {name}-restriction-len_limits is invalid. max_num must be >= min_num')

        if len(rest_errors) != 0:
            return False, rest_errors
        
        # Checking data to specified restrictions
        data_errors = []

        if data < min_num:
            data_errors.append(f'{name} integer {data} is too small. Minimum expected number is {min_num}')

        if data > max_num:
            data_errors.append(f'{name} integer {data} is too large. Maximum expected number is {max_num}')

        if len(data_errors) != 0:
            return False, data_errors

        return True, []


    def verify_email_data(cls: Self, name: str, data: Any) -> Tuple[bool, list]:
        '''
        This function will validate the incoming data
        to check if it is a valid email.

        cls (Self): the verification class
        name (str): the name of the data
        data (Any): the data to be verified

        return (bool, list): returns a success flag and a list of errors detected
        '''

        if type(data) != str:
            return False, [f'{name} type is invalid. Expected str but received {type(data).__name__}']

        if data.count('@') != 1:
            return False, [f'{name} is invalid. Email must only contain one @']

        email_parts = data.split('@')
        success, errors = cls.verify_string_data('Email', email_parts[0], { 'min_len': 1, 'max_len': 63 })

        if not success:
            return False, errors

        try:
            dns.resolver.resolve(email_parts[1], 'MX')

        except dns.resolver.NoAnswer:
            return False, [f'{name} was unable to be verified']

        except dns.resolver.NXDOMAIN:
            return False, [f'{name} has an invalid domain']

        return True, []


    def verify_uuid4_string(cls: Self, name: str, data: Any) -> Tuple[bool, list]:
        '''
        This function will validate the incoming data
        to check if it is a valid uuid.

        cls (Self): the verification class
        name (str): the name of the data
        data (Any): the data to be verified

        return (bool, list): returns a success flag and a list of errors detected
        '''

        if type(data) != str:
            return False, [f'{name} type is invalid. Expected str but received {type(data).__name__}']
        
        uuid_len = len(data)

        if uuid_len != 36:
            return False, [f'uuid {name} length is not 36']
        
        if not(data[8] == data[13] == data[18] == data[23] == '-') or data.count('-') != 4:
            return False, [f'uuid {name} incorrectly formatted']

        if not data[14] == '4':
            return False, [f'uuid {name} received version uuid{data[14]}. Expected version uuid4']

        if not data[19] in ['8','9','a','b']:
            return False, [f'uuid {name} variant invalid']
        
        try:
            uuid.UUID(data, version=4)

        except ValueError:
            return False, [f'uuid {name} unable to convert to uuid']
        
        finally:
            return True, []


    def verify_unix(
            cls: Self,
            name: str,
            data: Any,
            restrictions: dict={}
        ) -> Tuple[bool, list]:

        '''
        This function verifies whether the unix time is between the defined
        time values in relation to the current time.
        The restrictions is built to be flexible by utilising the format to
        modify the value into seconds, making it more easily understandable.
        It is not mandatory to pass through all the restrictions that
        are enforced onto the string.
        You can pass through an empty restrictions dict which will then
        default all the restrictions to their standard parameters.

        Example Restriction: -

        restrictions = {
            allow_future: "TRUE",
            max_time: {
                future: "TRUE",
                format: "HOURS",
                value: 8
            }
        }

        This checks whether the time provided is between
        the present and 8 hours into the future.

        Available Restrictions:
        - **allow_future (str)**:
            - DEFAULT = 'NONE'
            - Determines whether future times are considered valid.

        - **allow_past (str)**:
            - DEFAULT = 'NONE'
            - Determines whether past times are considered valid.

        - **min_time (dict)**:
            - Specifies the minimum allowable time value.
            - **Overrides:** If `current_time` is specified, it takes precedence over all other fields.
            - **Fields**:
                - **current_time (bool)**:
                    - DEFAULT = False
                    - If True, the current system time is used as the minimum.
                - **future (str)**:
                    - DEFAULT = 'NONE'
                    - Specifies whether the value should be applied to the future.
                - **past (str)**:
                    - DEFAULT = 'NONE'
                    - Specifies whether the value should be applied to the past.
                - **format (str)**:
                    - DEFAULT = "SECONDS"
                    - Specifies what unit of time to use.
                - **value (int)**:
                    - DEFAULT = 0
                    - An integer in the specified `format` stating how long from the current time the value is.

        - **max_time (dict)**:
            - Specifies the maximum allowable time value.
            - **Fields**:
                - **future (str)**:
                    - DEFAULT = 'NONE'
                    - Specifies whether the value should be applied to the future.
                - **past (str)**:
                    - DEFAULT = 'NONE'
                    - Specifies whether the value should be applied to the past.
                - **format (str)**:
                    - DEFAULT = "SECONDS"
                    - Specifies what unit of time to use.
                - **value (int)**:
                    - DEFAULT = INFINITY
                    - An integer in the specified `format` stating how long from the current time the value is.

        cls (Self): the verification class
        name (str): the name of the data
        data (Any): the data to be verified
        restrictions (dict): a dictionary of all the restrictions to apply [default - {}]

        return (bool, list): returns a success flag and a list of errors detected
        '''

        def convert_unix_restr_to_limit(time_dir, format, value):
            '''
            
            '''

            multiplier = 0
            current_time = int(datetime.now(timezone.utc).timestamp())

            if format == UnixNumberFormatEnum.SECONDS:
                multiplier = 1

            elif format == UnixNumberFormatEnum.MINUTES:
                multiplier = 60

            elif format == UnixNumberFormatEnum.HOURS:
                multiplier = 60 * 60

            elif format == UnixNumberFormatEnum.DAYS:
                multiplier = 60 * 60 * 24

            elif format == UnixNumberFormatEnum.YEARS:
                multiplier = round(60 * 60 * 24 * 365.25)

            return current_time + ((value * multiplier) * time_dir)

        if type(data) != int:
            return False, [f'{name} type is invalid. Expected int but received {type(data).__name__}']


        current_time = int(datetime.now(timezone.utc).timestamp())
        
        min_time = current_time
        max_time = current_time
        
        allow_future = NullBooleanEnum.FALSE
        allow_past = NullBooleanEnum.FALSE

        if 'allow_future' in restrictions:
            allow_future = NullBooleanEnum.from_value(restrictions['allow_future'])

        if 'allow_past' in restrictions:
            allow_past = NullBooleanEnum.from_value(restrictions['allow_past'])

        if None in [allow_future, allow_past]:
            return False, [f'DEV ERROR: Invalid Enum Value Provided']
        
        if allow_future == allow_past == NullBooleanEnum.FALSE:
            return False, [f'DEV ERROR: Filter must allow either past or future']

        if allow_future == NullBooleanEnum.FALSE:
            if data > current_time:
                return False, [f'{name} unix time cannot be set in the future']
            
        elif allow_future == NullBooleanEnum.TRUE:
            max_time = INFINITY
            
        if allow_past == NullBooleanEnum.FALSE:
            if data < current_time:
                return False, [f'{name} unix time cannot be set in the past']
        
        elif allow_past == NullBooleanEnum.TRUE:
            max_time = 0

        min_current_time = False
        min_future = NullBooleanEnum.NONE
        min_past = NullBooleanEnum.NONE
        min_format = UnixNumberFormatEnum.SECONDS
        min_value = 0

        max_future = NullBooleanEnum.NONE
        max_past = NullBooleanEnum.NONE
        max_format = UnixNumberFormatEnum.SECONDS
        max_value = INFINITY

        if 'min_time' in restrictions: 
            min_restr = restrictions['min_time']

            if 'current_time' in min_restr:
                min_current_time = bool(min_restr['current_time'])

            if 'future' in min_restr:
                min_future = NullBooleanEnum.from_value(min_restr['future'])

            if 'past' in min_restr:
                min_past = NullBooleanEnum.from_value(min_restr['past'])

            if 'format' in min_restr:
                min_format = UnixNumberFormatEnum.from_value(min_restr['format'])

            elif not min_current_time:
                return False, [f'DEV ERROR: {name} unix min_time restriction must have a format if current time not set']

            if 'value' in min_restr:
                min_value = min_restr['value']

            elif not min_current_time:
                return False, [f'DEV ERROR: {name} unix min_time restriction must have a value if current time not set']

        if 'max_time' in restrictions:
            max_restr = restrictions['max_time']

            if 'future' in max_restr:
                max_future = NullBooleanEnum.from_value(max_restr['future'])

            if 'past' in max_restr:
                max_past = NullBooleanEnum.from_value(max_restr['past'])

            if 'format' in max_restr:
                max_format = UnixNumberFormatEnum.from_value(max_restr['format'])

            else:
                return False, [f'DEV ERROR: {name} unix max_time restriction must have a format']

            if 'value' in max_restr:
                max_value = max_restr['value']

            else:
                return False, [f'DEV ERROR: {name} unix max_time restriction must have a value']

        if min_future == NullBooleanEnum.TRUE or max_future == NullBooleanEnum.TRUE:
            if min_future != max_future and not min_current_time:
                return False, [f'DEV ERROR: {name} unix future restriction for min/max must both be set to TRUE']

            if min_past == NullBooleanEnum.TRUE or max_past == NullBooleanEnum.TRUE:
                return False, [f'DEV ERROR: {name} unix restriction for min/max past cannot be set to TRUE when min/max future is set to TRUE']

            if allow_future == NullBooleanEnum.FALSE:
                return False, [f'DEV ERROR: {name} unix restriction for min/max future cannot be set to TRUE when future unix is not allowed']

            if not min_current_time:
                min_time = convert_unix_restr_to_limit(1, min_format, min_value)

            max_time = convert_unix_restr_to_limit(1, max_format, max_value)

            if min_time >= max_time:
                return False, [f'DEV ERROR: {name} unix future restriction min limit ({min_time}) greater than max limit ({min_time})']

            if min_time > data:
                return False, [f'{name} unix out of range (PAST)']

            if data > max_time:
                return False, [f'{name} unix out of range (FUTURE)']

        if min_past == NullBooleanEnum.TRUE or max_past == NullBooleanEnum.TRUE:
            if min_past != max_past and not min_current_time:
                return False, [f'DEV ERROR: {name} unix past restriction for min/max must both be set to TRUE']

            if allow_past == NullBooleanEnum.FALSE:
                return False, [f'DEV ERROR: {name} unix restriction for min/max past cannot be set to TRUE when past unix is not allowed']

            if not min_current_time:
                min_time = convert_unix_restr_to_limit(-1, min_format, min_value)

            max_time = convert_unix_restr_to_limit(-1, max_format, max_value)

            if min_time <= max_time:
                return False, [f'DEV ERROR: {name} unix past restriction min limit ({min_time}) greater than max limit ({min_time})']

            if min_time < data:
                return False, [f'{name} unix out of range (PAST)']

            if data < max_time:
                return False, [f'{name} unix out of range (FUTURE)']

        return True, []


    # TODO: Rework Needed (Function Similarlly To verify_unix Restrictions)
    def verify_datetime_string(
            cls: Self,
            name: str,
            data: Any,
            restrictions: dict={}
        ) -> Tuple[bool, list]:

        '''
        With the relevant restrictions and data, this function will verify
        the specified data checking that it is a valid datetime and return the
        necessary errors if any.
        It is not mandatory to pass through all the restrictions that
        are enforced onto the datetime.
        You can pass through an empty restrictions dict which will then
        default all the restrictions to their standard parameters.

        Example Restriction: -

        restrictions = {
            date: {
                min_date: "2025-01-01",
                max_date: "2025-12-31"
            }
        }

        Available Restrictions:
        - **date (dict)**:
            - Specifies restrictions related to calendar dates.
            - **Fields**:
                - **min_date (str)**:
                    - DEFAULT = 100 years in the past
                    - The earliest allowed date in string format (e.g., "2025-01-01").
                    - Must be in a consistent and parseable format (e.g., ISO 8601).
                - **max_date (str)**:
                    - DEFAULT = 100 years in the future
                    - The latest allowed date in string format (e.g., "2025-12-31").
                    - Must be in a consistent and parseable format (e.g., ISO 8601).

        - **time (dict)**:
            - Specifies restrictions related to time of day.
            - **Fields**:
                - **min_time (str)**:
                    - DEFAULT = 00:00:00
                    - The earliest allowed time in string format (e.g., "08:00").
                    - Must follow a standard time format such as "HH:MM" or "HH:MM:SS".
                - **max_time (str)**:
                    - DEFAULT = 23:59:59
                    - The latest allowed time in string format (e.g., "18:00").
                    - Must follow a standard time format such as "HH:MM" or "HH:MM:SS".

        cls (Self): the verification class
        name (str): the name of the data
        data (Any): the data to be verified
        restrictions (dict): a dictionary of all the restrictions to apply [default - {}]

        return (bool, list): returns a success flag and a list of errors detected
        '''


        def check_data_format(data, _format):
            try:
                data_object = datetime.strptime(data, _format)

                return True, data_object

            except:
                return False, None

        if type(data) != str:
            return False, [f'{name} type is invalid. Expected str but received {type(data).__name__}']
        
        data_object = 0
        today = datetime.today()

        _date = False      
        min_date = today.replace(year=today.year - 100).strftime("%Y-%m-%d")
        max_date = today.replace(year=today.year + 100).strftime("%Y-%m-%d")

        _time = False
        min_time = '00:00:00'
        max_time = '23:59:59'

        if 'date' in restrictions:
            _date = True

            if 'min' in restrictions['date']:
                min_date = restrictions['date']['min']

            if 'max' in restrictions['date']:
                max_date = restrictions['date']['max']

        if 'time' in restrictions:
            _time = True

            if 'min' in restrictions['time']:
                min_time = restrictions['time']['min']

            if 'max' in restrictions['time']:
                max_time = restrictions['time']['max']

        min_val = 0
        max_val = 0
        success = None

        if _date and _time:
            min_val = datetime.strptime(f'{min_date} {min_time}', "%Y-%m-%d %H:%M:%S")
            max_val = datetime.strptime(f'{max_date} {max_time}', "%Y-%m-%d %H:%M:%S")

            success, data_object = check_data_format(data, "%Y-%m-%d %H:%M:%S")

        elif _date:
            min_val = datetime.strptime(f'{min_date}', "%Y-%m-%d")
            max_val = datetime.strptime(f'{max_date}', "%Y-%m-%d")

            success, data_object = check_data_format(data, "%Y-%m-%d")

        elif _time:
            min_val = datetime.strptime(f'{min_time}', "%H:%M:%S")
            max_val = datetime.strptime(f'{max_time}', "%H:%M:%S")

            success, data_object = check_data_format(data, "%H:%M:%S")

        if not success:
            return False, [f'{name} invalid datetime format. Expected YYYY-MM-DD']

        if (min_val > data_object) and (max_val < data_object):
            return False, [f'{name} datetime out of range']
        
        return True, []
