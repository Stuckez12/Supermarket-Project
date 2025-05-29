'''
Fetching and modifying yaml file schemas.
Used to define all restrictions on incoming parameters and other uses.
'''

import yaml

from typing import Tuple, Union


def load_yaml_file_as_dict(direc: str) -> dict:
    '''
    Receives the directory of the specified yaml file, loads the data, and returns as a dict.

    direc (str): the location of the yaml file

    return (dict): the yaml file as a dictionary
    '''

    with open(direc) as file:
        schemas = yaml.safe_load(file)

    return schemas


def insert_data_into_schema(schema: dict, data: dict) -> Tuple[bool, Union[dict, None]]:
    '''
    Inserts the data into the given schema and assigns it to be checked.

    schema (dict): the dict add the data to
    data (dict): a dictionary of the data to add to the schema

    return (bool, [dict, None]): returns a success flag and the modified data
    '''

    try:
        for field, field_data in schema.items():
            extracted_data = data.get(field)
            field_data['data'] = extracted_data

            if extracted_data is not None:
                field_data['check'] = True

            else:
                field_data['check'] = False

        return True, schema
    
    except (AttributeError, TypeError):
        return False, None


def format_schema_data_types(schema: dict, to_string: bool=True) -> dict:
    '''
    Converts the type of data to a string, making it more manageable.

    schema (dict):  the dict with the data types
    to_string (bool): whether to convert types to strings

    return (bool, [dict, None]): returns a success flag and the modified data
    '''

    type_map = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'email': 'email',
        'str_uuid': 'str_uuid',
        'unix': 'unix',
    }

    for _, field_data in schema.items():
        if to_string:
            if isinstance(field_data['type'], type):
                field_data['type'] = field_data['type'].__name__
        else:
            if isinstance(field_data['type'], str):
                field_data['type'] = type_map.get(field_data['type'], field_data['type'])

    return schema


def get_verification_schema(config: dict, data: dict) -> Tuple[bool, str, Union[dict, None]]:
    '''
    Fetches a formatted schema with the relevant data
    to be used for data validation.

    config (dict): the foundational schema to be modified and completed
    data (dict): the data to be inserted into the schema

    return (bool, str, [dict, None]): returns a success flag, a message and the data
    '''

    if config is None:
        return False, 'Server Error: Required Schema Not Downloaded', None

    status, schema = insert_data_into_schema(config, data)

    if not status:
        return False, 'Server Error: Imported Schema Incorrectly Formatted', None

    return True, '', format_schema_data_types(schema, to_string=False)
