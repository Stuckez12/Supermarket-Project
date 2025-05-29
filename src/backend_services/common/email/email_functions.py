import os

from python_http_client.exceptions import UnauthorizedError, ForbiddenError, \
    BadRequestsError, InternalServerError, ServiceUnavailableError, TooManyRequestsError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Tuple

from src.backend_services.common.email.format_http_files import format_html_template
from src.backend_services.common.email.otp_functions import create_otp


SENDGRID_EMAIL_API = os.environ.get('SENDGRID_EMAIL_API')
SENDGRID_CLIENT = SendGridAPIClient(SENDGRID_EMAIL_API)
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
DEBUG_SEND_EMAIL = int(os.environ.get('DEBUG_SEND_EMAILS'))


def create_email(
        to_emails: list[str],
        subject: str,
        from_email: str=EMAIL_SENDER,
        plain_context: str=None,
        html_context: str=None
    ) -> Mail:

    '''
    This creates an email using sendgrids module.

    to_emails (list[str]): list of all end users to receive the email
    subject (str): the subject of the email
    from_email (str): who is sending the email [default - EMAIL_SENDER]
    plain_context (str): basic plain text in the body of the email [default - None]
    html_context (str): html file as a string for the email body [default - None]
    '''

    email = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=plain_context,
        html_content=html_context
    )

    return email


def send_email(email: Mail) -> Tuple[bool, int, str]:
    '''
    Sends the Mail created beforehand using the sendgrid API

    email (Mail): the Mail object containing the emails contents

    return (bool, int, str): success flag, http status and message
    '''

    success = False
    http_code = 202
    message = 'Email Sent Successfully'

    if not DEBUG_SEND_EMAIL:
        return True, 202, message

    try:
        SENDGRID_CLIENT.send(email)
        success = True

    except UnauthorizedError:
        http_code = 401
        message = 'DEV ERROR: API key is missing or invalid'

    except ForbiddenError:
        http_code = 403
        message = 'Specified Sender Is Forbidden'

    except BadRequestsError:
        http_code = 400
        message = 'The provided data is either not formatted correctly or missing'

    except InternalServerError:
        http_code = 500
        message = 'SendGrid Error: Service unable to process request'

    except ServiceUnavailableError:
        http_code = 503
        message = 'SendGrid Error: Service not accepting requests currently'

    except TooManyRequestsError:
        http_code = 429
        message = 'Maximum Daily Emails Sent Reached Or Sending Too Many Requests At Once'

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

    success, code, message = send_email(email)

    if not success:
        return success, None, message

    return success, otp_id, message
