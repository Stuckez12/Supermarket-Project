import yaml


def load_yaml_file_as_dict(direc):
    with open(direc) as file:
        schemas = yaml.safe_load(file)

    return schemas


def insert_data_into_schema(schema, data):
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


def format_schema_data_types(schema, to_string=True):
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


def get_verification_schema(CONFIG, data):
    if CONFIG is None:
        return False, 'Server Error: Required Schema Not Downloaded', None

    status, schema = insert_data_into_schema(CONFIG, data)

    if not status:
        return False, 'Server Error: Imported Schema Incorrectly Formatted', None

    return True, '', format_schema_data_types(schema, to_string=False)
