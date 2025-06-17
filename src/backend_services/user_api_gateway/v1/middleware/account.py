'''

'''

import json

from fastapi import HTTPException, Cookie

from src.backend_services.common.redis.user_sessions import check_session


async def is_user_logged_in(
        session: str = Cookie(default=None),
        user: str = Cookie(default=None)
    ) -> None:

    '''
    Checks whether the user is logged in with valid cookies and data.

    session (str): the session object containing the session_uuid and expiry time [default - No Cookie]
    user (str): the user object containing the users public data [default - No Cookie]

    return (None):
    '''

    if None in [session, user]:
        raise HTTPException(status_code=401, detail='You Must Be Logged In To Perform This Action')

    try:
        user_dict = json.loads(user)
        session_dict = json.loads(session)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Cookies Provided Incorrectly Formatted')

    success, message = check_session(session_dict.get('session_uuid'), user_dict.get('uuid'))

    if not success:
        raise HTTPException(status_code=400, detail=message)
