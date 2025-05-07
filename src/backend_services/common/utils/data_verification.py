from enum import Enum
from math import inf as INFINITY


# May be moved to seperate file
class CharReqEnum(Enum):
    MUST = 'MUST'
    DEFAULT = 'DEFAULT'
    NONE = 'NONE'


    @classmethod
    def from_name(cls, name):
        return cls.members.get(name.upper())


    @classmethod
    def from_value(cls, value):
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


    def set_min_restriction(cls, name, data, restrictions, rest_errors):
        '''
        This function sets the minimum length a variable can be.  
        '''

        if 'min_len' in restrictions:
            if restrictions['min_len'] > 0:
                return restrictions['min_len'], rest_errors

            else:
                rest_errors.append(f'DEV ERROR: {name}-restriction-min_len is invalid. min_len must be a positive int')

        return data, rest_errors

    
    def set_max_restriction(cls, name, data, restrictions, rest_errors):
        '''
        This function sets the maximum length a variable can be. 
        '''

        if 'max_len' in restrictions:
            if restrictions['max_len'] > 0:
                return restrictions['max_len'], rest_errors

            else:
                rest_errors.append(f'DEV ERROR: {name}-restriction-max_len is invalid. max_len must be a positive int')

        return data, rest_errors


    def set_data_type_restriction(cls, name, restrictions, limit_to, rest_errors):
        '''
        This function sets the variable in the restrictions
        to the desired data type to check against.
        If it is unable to find the desired data type, it defaults
        to the first data type that is provided to the function.
        '''

        if 'type' in restrictions:
            if restrictions['type'] in limit_to:
                return restrictions['type'], rest_errors

            else:
                rest_errors.append(f'DEV ERROR: {name}-restriction-type is invalid. Data type must be within specified limit {limit_to}')

        return limit_to[0], rest_errors

        
    def set_enum_restriction(cls, name, ClassEnum: any, restrictions: dict, value: str, errors: list):
        '''
        This function converts an ENUM string to the class representation.
        If the specified value is not present in the restrictions, it
        assigns the output to the DEFAULT class value.
        '''

        if value in restrictions:
            new_val = ClassEnum.from_value(restrictions[value])

            if new_val is None:
                errors.append(f'DEV ERROR: {name}-restriction-{value} is invalid. {value} must be a value within CharReqEnum')

            return new_val, errors

        return ClassEnum.DEFAULT, errors


    def validate_char_requirement(cls, data, char_check_fn, requirement, name, char_req, data_errors):
        '''
        This function checks whether the characters (specified
        by the provided function) are present within a string.
        It uses the CharReqEnum state to check whether the characters
        should be present in the string or not included.
        '''

        if requirement == CharReqEnum.DEFAULT:
            return data_errors

        has_char = any(char_check_fn(char) for char in data)

        if has_char and requirement == CharReqEnum.NONE:
            data_errors.append(f'{name} must not contain {char_req}')

        elif not has_char and requirement == CharReqEnum.MUST:
            data_errors.append(f'{name} must contain at least one {char_req}')

        return data_errors


    def validate_email_requirement(cls, data, requirement, name, data_errors):
        '''
        This custom function checks whether the character '@'
        is present within a string.
        It uses the CharReqEnum state to check whether it
        should be present in the string or not included.
        '''

        has_at = '@' in data

        if has_at and requirement == CharReqEnum.NONE:
            data_errors.append(f'{name} must not contain \'@\'')

        elif not has_at and requirement == CharReqEnum.MUST:
            data_errors.append(f'{name} must contain \'@\'')

        return data_errors


    def verify_data(cls: any, data: dict) -> tuple[bool, list]:
        '''
        This function recieves nested dictionaries containing the
        variables and the expected data type and restrictions for
        each variable.

        Example string input: -

        data = {
            variable_name: {
                type: str,
                data: "hello",
                restrictions: {
                    min_len: 4,
                    max_len: 8,
                    lower_case: "MUST",
                    upper_case: "MUST",
                    numbers: "DEFAULT",
                    symbols: "NONE",
                    email: "DEFAULT"
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

        cls (any): 
        data (dict): 

        return (any): 
        '''

        total_errors = []

        for variable, data_points in data.items():
            success = True
            errors = []

            data = data_points['data']

            if 'restrictions' in data_points:
                restrictions = data_points['restrictions']

            if data_points['type'] == str:
                success, errors = cls.verify_string_data(variable, data, restrictions)
            
            elif data_points['type'] in [int, float]:
                restrictions['type'] = data_points['type']
                success, errors = cls.verify_number_data(variable, data, restrictions)

            if len(errors) != 0 and not success:
                total_errors += errors

        if len(total_errors) != 0:
            return False, total_errors
        
        return True, []


    def verify_string_data(cls: any, name: str, data: any, restrictions: dict={}) -> tuple[bool, list]:
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
            email: "DEFAULT"
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

        - **email (str)**: 
            - DEFAULT = "DEFAULT"
            - Accepts the `CharacterRequirementStatus` Enum.
            - Determines whether the string must contain an "@" character (used for email validation).


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

        cls (any): the DataVerification class
        name (str): the name of the data (variable name?)
        data (any): the data to be verified
        restrictions (dict): a dictionary of all the restrictions that can be applied

        return (bool, list): returns the status of the string check and a list of all the errors with the data
        '''

        if type(data) != str:
            return False, [f'{name} type is invalid. Expected str but recieved {type(data).__name__}']
        
        # Default Restrictions
        min_len = 0
        max_len = INFINITY
        lower_case = CharReqEnum.DEFAULT
        upper_case = CharReqEnum.DEFAULT
        numbers = CharReqEnum.DEFAULT
        symbols = CharReqEnum.DEFAULT
        email = CharReqEnum.DEFAULT

        rest_errors = []

        # Formatting Restrictions
        min_len, rest_errors = cls.set_min_restriction(name, min_len, restrictions, rest_errors)
        max_len, rest_errors = cls.set_max_restriction(name, max_len, restrictions, rest_errors)
        lower_case, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'lower_case', rest_errors)
        upper_case, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'upper_case', rest_errors)
        numbers, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'numbers', rest_errors)
        symbols, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'symbols', rest_errors)
        email, rest_errors = cls.set_enum_restriction(name, CharReqEnum, restrictions, 'email', rest_errors)

        if max_len < min_len:
            rest_errors.append(f'DEV ERROR: {name}-restriction-len_limits is invalid. max_len must be >= min_len')

        if len(rest_errors) != 0:
            return False, rest_errors
        
        data_errors = []

        # Checking data to specified restrictions
        data_len = len(data)

        if data_len < min_len:
            data_errors.append(f'{name} string length of {data_len} is too short. Minimum expected length is {min_len} characters')

        if data_len > max_len:
            data_errors.append(f'{name} string length of {data_len} is too long. Maximum expected length is {max_len} characters')

        def is_symbol(char):
            return not char.isalnum() and char != '@'

        data_errors = cls.validate_char_requirement(data, str.islower, lower_case, name, 'lower_case', data_errors)
        data_errors = cls.validate_char_requirement(data, str.isupper, upper_case, name, 'upper_case', data_errors)
        data_errors = cls.validate_char_requirement(data, str.isdigit, numbers,    name, 'number',     data_errors)
        data_errors = cls.validate_char_requirement(data, is_symbol,   symbols,    name, 'symbol',     data_errors)
        data_errors = cls.validate_email_requirement(data, email, name, data_errors)

        if len(data_errors) != 0:
            return False, data_errors

        return True, []


    def verify_number_data(cls, name, data, restrictions={}):
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
        '''

        # Default Restrictions
        min_num = -INFINITY
        max_num = INFINITY

        rest_errors = []

        # Formatting Restrictions
        data_type, rest_errors = cls.set_data_type_restriction(name, restrictions, [int, float], rest_errors)
        min_num, rest_errors = cls.set_min_restriction(name, min_num, restrictions, rest_errors)
        max_num, rest_errors = cls.set_max_restriction(name, max_num, restrictions, rest_errors)

        print("Min: " + min_num)
        print("Max: " + max_num)

        if data_type.__name__ == 'float':
            try:
                data = float(data)

            except:
                return False, [f'{name} type is invalid. Expected {data_type.__name__} but recieved {type(data).__name__}']

        if type(data).__name__ != data_type.__name__:
            return False, [f'{name} type is invalid. Expected {data_type.__name__} but recieved {type(data).__name__}']

        if max_num < min_num:
            rest_errors.append(f'DEV ERROR: {name}-restriction-len_limits is invalid. max_num must be >= min_num')

        if len(rest_errors) != 0:
            return False, rest_errors
        
        # Checking data to specified restrictions
        data_errors = []

        if data < min_num:
            data_errors.append(f'{name} integer {data} is too small. Minimum expected number is {min_num}')

        if data > max_num:
            data_errors.append(f'{name} integer {data} is too large. Maximum expected number is {max_len}')

        if len(data_errors) != 0:
            return False, data_errors

        return True, []
