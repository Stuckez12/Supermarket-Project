'''
This file contains all custom exceptions used throughout the project.
'''

from typing import Self


class EmailAPIError(Exception):
    '''
    This is a custom error handling class relating to the handling of emails.
    '''

    def __init__(cls: Self, message: str) -> None:
        '''
        Initialises the class and prints out the provided message
        whilst calling traceback of the errors source.

        cls (Self): The specified class self
        message (str): The message to output after traceback

        return (None):
        '''

        super().__init__(message)
    

    @classmethod
    def email_send_limit_exceeded(cls: Self, format: str, limit: int) -> Self:
        '''
        Formats a message specifying the email limiting error.

        cls (Self): The specified class self
        format (str): the unit of time to use to track email deliveries.
        limit (int): The max amount of emails to send following the specified format.

        return (Self): returns the initialisation of itself
        '''

        message = f'''[EMAIL API ERROR]: Unable to send email. 

Can only send {limit} emails every {format}.
Please try again later.'''

        return cls(message)
