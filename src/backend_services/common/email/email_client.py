import os

from azure.communication.email import EmailClient as AzureEmailClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from datetime import datetime
from typing import Self, Tuple, Union

from src.backend_services.common.email.format_http_files import format_html_template
from src.backend_services.common.email.otp_functions import create_otp
from src.backend_services.common.exceptions.emailing import EmailAPIError


class EmailClient():
    '''
    This class is used to send emails to the specified
    receivers. This class contains all the necessary
    unique functions to send the desired email with
    just one function call, simplifying the process
    and making it easily reusable.

    The external service this class uses is Microsoft
    Azure Communication Service. It contacts the created
    resource on Azures' side and request them to send
    out an email to the desired recipients.
    '''

    def __init__(
            cls: Self,
            endpoint: str,
            credential: str,
            email_sender: str,
            debug_settings: dict=None
        ) -> None:

        '''
        Initialising the client to be ready to send emails.

        cls (Self): the EmailClient class
        endpoint (str): the url to the specified azure resource
        credential (str): the access credential key for authorisation
        email_sender (str): who is sending the email
        debug_settings (dict): debug settings controlling/restricting the EmailClient

        return (None):
        '''

        cls.endpoint = endpoint
        cls.credential = AzureKeyCredential(credential)
        cls.client = AzureEmailClient(cls.endpoint, cls.credential)

        cls.sender = email_sender

        # Class debug settings
        debug_settings = debug_settings or {}

        if debug_settings == {}:
            return

        ## Sending emails debug
        cls.enable_sending_emails = bool(int(debug_settings.get('send_email', 0)))
        cls.max_email_send_per_day = debug_settings.get('max_email_send_per_day', 100)
        cls.max_email_send_per_minute = debug_settings.get('max_email_send_per_minute', 10)

        cls.current_emails_sent_per_day = 0
        cls.current_emails_sent_per_minute = 0

        cls.current_day = datetime.now().day
        cls.current_minute = datetime.now().minute


    def _create_new_email(
            cls: Self,
            to_emails: list[str],
            subject: str,
            from_email: str=None,
            plain_context: str=None,
            html_context: str=None
        ) -> dict:

        '''
        This creates an email in the format accepted by Microsoft Azure.

        cls (Self): the EmailClient class
        to_emails (list[str]): list of all end users to receive the email
        subject (str): the subject of the email
        from_email (str): who is sending the email [default - None]
        plain_context (str): basic plain text in the body of the email [default - None]
        html_context (str): html file as a string for the email body [default - None]

        return (dict): formatted email to send to Azure
        '''

        from_email = from_email or cls.sender

        recipients = []

        for email in to_emails:
            recipients.append({ 'address': email })

        email_data = {
            "senderAddress": from_email,
            "recipients": {
                "to": recipients
            },
            "content": {
                "subject": subject,
                "plainText": plain_context,
                "html": html_context
            }
        }

        print(email_data)

        return email_data


    def _send_email(cls: Self, email_data: dict) -> Tuple[bool, int, str]:
        '''
        Sends the email data created beforehand using the Microsoft Azure API

        cls (Self): the EmailClient class
        email_data (dict): the Mail object containing the emails contents

        return (bool, int, str): success flag, http status and message
        '''

        success = False
        http_code = 202
        message = 'Email Sent Successfully'

        if not cls.enable_sending_emails:
            return True, http_code, 'Sending Emails Disabled'

        try:
            print('Sending Email')
            print(cls.enable_sending_emails)
            print()
            cls._update_internal_emails_sent_data()
            cls.client.begin_send(email_data)
            success = True

        except HttpResponseError as e:
            print(e)
            http_code = 502
            message = 'External Service Unable To Send Email'

        except ServiceRequestError:
            http_code = 503
            message = 'Unable To Connect To Azure Emailing Service'

        except ClientAuthenticationError:
            http_code = 503
            message = 'Unable To Authenticate Self'

        except (ValueError, TypeError):
            http_code = 500
            message = 'Server Is Unable To Send Email'

        except EmailAPIError as err:
            http_code = 500
            message = str(err)

        except Exception:
            http_code = 500
            message = 'An Unknown Error Occured Whilst Attempting To Send Email'

        return success, http_code, message


    def _update_internal_emails_sent_data(cls: Self):
        '''
        Sends the email data created beforehand using the Microsoft Azure API

        cls (Self): the EmailClient class

        return (None): an error will be raised instead when the set limit has been reached 
        '''

        email_limits = {
            'day': {
                'current_time': cls.current_day,
                'current_value': cls.current_emails_sent_per_day,
                'max_limit': cls.max_email_send_per_day
            },
            'minute': {
                'current_time': cls.current_minute,
                'current_value': cls.current_emails_sent_per_minute,
                'max_limit': cls.max_email_send_per_minute
            }
        }

        for key, value in email_limits.items():
            current_time = getattr(datetime.now(), key)

            if current_time != value['current_time']: # Reset limit tracking if the time has passed
                setattr(cls, 'current_' + key, current_time)
                setattr(cls, 'current_emails_sent_per_' + key, 0)

                continue

            if int(value['current_value']) >= int(value['max_limit']):
                raise EmailAPIError.email_send_limit_exceeded(key, value['max_limit'])

        for key in email_limits.keys(): # Increment limits
            current_val = int(getattr(cls, 'current_emails_sent_per_' + key))

            setattr(cls, 'current_emails_sent_per_' + key, current_val + 1)


    def send_otp_email(cls: Self, send_to: list) -> Tuple[bool, int, str, Union[str, None]]:
        '''
        Creates and sends an email containing the OTP code for
        the user to use to verify their account.

        cls (Self): the EmailClient class
        send_to (list): who to send the email to

        return (bool, int, str, str): success flag, status, message and OTP ID
        '''

        code, otp_id = create_otp()

        print('OTP Data:', send_to, code, otp_id)

        html_format = { '{{OTP_CODE}}': code }
        otp_template = format_html_template('src/backend_services/common/email/http_email_files/otp_verification.html', html_format)

        email_data = cls._create_new_email(send_to, 'Verify Your Account', html_context=otp_template)

        success, http_status, message = cls._send_email(email_data)

        print('Email Sent Result')
        print(success, http_status, message)

        if not success:
            return success, http_status, message, None

        return success, http_status, message, otp_id


# Configure email client
debug_settings = {
    'send_email': os.environ.get('DEBUG_SEND_EMAILS'),
    'max_email_send_per_day': os.environ.get('DEBUG_SEND_EMAIL_DAY_LIMIT'),
    'max_email_send_per_minute': os.environ.get('DEBUG_SEND_EMAIL_MINUTE_LIMIT')
}

email_client = EmailClient(
    os.environ.get('EMAIL_ENDPOINT'),
    str(os.environ.get('EMAIL_CREDENTIAL')),
    os.environ.get('EMAIL_SENDER'),
    debug_settings=debug_settings
)
