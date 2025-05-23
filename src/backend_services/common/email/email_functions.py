import os

from python_http_client.exceptions import UnauthorizedError, ForbiddenError, \
    BadRequestsError, InternalServerError, ServiceUnavailableError, TooManyRequestsError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.backend_services.common.email.format_http_files import format_html_template
from src.backend_services.common.email.otp_functions import create_otp, verify_otp


SENDGRID_EMAIL_API = os.environ.get('SENDGRID_EMAIL_API')
SENDGRID_CLIENT = SendGridAPIClient(SENDGRID_EMAIL_API)
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')


def create_email(to_emails, subject, from_email=EMAIL_SENDER, plain_context=None, html_context=None):
    '''
    
    '''

    email = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=plain_context,
        html_content=html_context
    )

    return email


def send_email(email):
    '''
    
    '''

    success = False
    http_code = 202
    message = 'Email Sent Successfully'

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


def generate_otp_email(send_to: list):
    '''
    
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
