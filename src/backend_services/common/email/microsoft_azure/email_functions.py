import os

from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from typing import Tuple

from src.backend_services.common.email.format_http_files import format_html_template
from src.backend_services.common.email.otp_functions import create_otp


MS_AZURE_EMAIL_ENDPOINT = os.environ.get('MS_AZURE_EMAIL_ENDPOINT')
MS_AZURE_EMAIL_CREDENTIAL = AzureKeyCredential(os.environ.get('MS_AZURE_EMAIL_CREDENTIAL'))
MS_AZURE_EMAIL_CLIENT = EmailClient(MS_AZURE_EMAIL_ENDPOINT, MS_AZURE_EMAIL_CREDENTIAL)

EMAIL_SENDER = os.environ.get('MS_AZURE_EMAIL_SENDER')
DEBUG_SEND_EMAIL = int(os.environ.get('DEBUG_SEND_EMAILS'))


def create_email(
        to_emails: list[dict],
        subject: str,
        from_email: str=EMAIL_SENDER,
        plain_context: str=None,
        html_context: str=None
    ) -> dict:

    '''
    This creates an email using sendgrids module.

    to_emails (list[str]): list of all end users to receive the email
    subject (str): the subject of the email
    from_email (str): who is sending the email [default - EMAIL_SENDER]
    plain_context (str): basic plain text in the body of the email [default - None]
    html_context (str): html file as a string for the email body [default - None]

    return (dict): formatted email to send to Azure
    '''

    message = {
        "senderAddress": from_email,
        "recipients": {
            "to": to_emails
        },
        "content": {
            "subject": subject,
            "plainText": plain_context,
            "html": html_context
        }
    }

    return message


def send_email(email: dict) -> Tuple[bool, int, str]:
    '''
    Sends the Mail created beforehand using the sendgrid API

    email (Mail): the Mail object containing the emails contents

    return (bool, int, str): success flag, http status and message
    '''

    success = False
    http_code = 202
    message = 'Email Sent Successfully'

    if not DEBUG_SEND_EMAIL:
        return True, http_code, message

    try:
        MS_AZURE_EMAIL_CLIENT.begin_send(email)
        success = True

    except HttpResponseError:
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

    except Exception:
        http_code = 500
        message = 'An Unknown Error Occured Whilst Attempting To Send Email'

    return success, http_code, message


def generate_otp_email(send_to: list) -> Tuple[bool, int, str]:
    '''
    Creates and sends an email containing the OTP code for
    the user to use to verify their account.

    send_to (list): who to send the email to

    return (bool, int, str): success flag, OTP ID and message
    '''

    code, otp_id = create_otp()

    print('OTP Data:', send_to, code, otp_id)

    html_format = { '{{OTP_CODE}}': code }
    otp_template = format_html_template('src/backend_services/common/email/http_email_files/otp_verification.html', html_format)

    email = create_email(send_to, 'Verify Your Account', html_context=otp_template)

    success, http_status, message = send_email(email)

    if not success:
        return success, http_status, message, None

    return success, http_status, message, otp_id
