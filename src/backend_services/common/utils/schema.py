import yaml



def load_yaml_file_as_dict(direc):
    with open(direc) as file:
        schemas = yaml.safe_load(file)

    return schemas


def insert_data_into_schema(schema, data):
    for field, field_data in schema.items():
        field_data['data'] = data.get(field)

    return schema

def format_schema_data_types(schema, to_string=True):
    type_map = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict
        # Add other types as needed
    }

    for field, field_data in schema.items():
        if to_string:
            if isinstance(field_data['type'], type):
                field_data['type'] = field_data['type'].__name__
        else:
            if isinstance(field_data['type'], str):
                field_data['type'] = type_map.get(field_data['type'], field_data['type'])  # leave unchanged if unknown

    return schema



print(load_yaml_file_as_dict("src/backend_services/account/verification_config/registration.yaml"))

