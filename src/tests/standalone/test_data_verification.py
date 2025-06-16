'''
This file contains all the tests for the DataVerification class
'''

import json
import pytest

from typing import Any

from src.backend_services.common.utils.data_verification import DataVerification


VERIFY_CLASS = DataVerification()

STRING_RESTRICTIONS = []
NUMBER_RESTRICTIONS = []


with open('src/tests/standalone/test_data_verification.json', 'r') as file:
    tests = json.load(file)

    # Fetching String Tests
    for _, test_data in tests['Test_String_Validation'].items():
        data_type = eval(test_data['type'])
        data = data_type(test_data['data'])

        for res_test in test_data['func_iter']:
            STRING_RESTRICTIONS.append((data, res_test['restrictions'], tuple(res_test['func_result'])))

    # Fetching Number Tests
    for _, test_data in tests['Test_Number_Validation'].items():
        data_type = eval(test_data['type'])
        data = data_type(test_data['data'])

        for res_test in test_data['func_iter']:
            if 'type' in res_test['restrictions']:
                res_test['restrictions']['type'] = eval(res_test['restrictions']['type'])

            NUMBER_RESTRICTIONS.append((data, res_test['restrictions'], tuple(res_test['func_result'])))
    

@pytest.mark.parametrize("test_data, restrictions, expected_result", STRING_RESTRICTIONS)
def test_verify_string_data(test_data: Any, restrictions: dict, expected_result: tuple) -> None:
    '''
    This test checks the verification of a string ensuring
    that all restrictions are applied correctly and all
    error messages are returned.

    test_data (Any): the data to verify
    restrictions (dict): the restrictions to apply to the data
    expected_result (tuple): the expected output from the function

    return (None):
    '''

    result = VERIFY_CLASS.verify_string_data('Testing', test_data, restrictions=restrictions)
    assert result == expected_result


@pytest.mark.parametrize("test_data, restrictions, expected_result", NUMBER_RESTRICTIONS)
def test_verify_number_data(test_data: Any, restrictions: dict, expected_result: tuple) -> None:
    '''
    This test checks the verification of an integer/float ensuring
    that all restrictions are applied correctly and all
    error messages are returned.

    test_data (Any): the data to verify
    restrictions (dict): the restrictions to apply to the data
    expected_result (tuple): the expected output from the function

    return (None):
    '''

    result = VERIFY_CLASS.verify_number_data('Testing', test_data, restrictions=restrictions)
    assert result == expected_result
