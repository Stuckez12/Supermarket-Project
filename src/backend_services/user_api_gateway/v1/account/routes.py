from fastapi import APIRouter


router = APIRouter()


@router.post("/register")
async def register_user(email, password, first_name, last_name, date_of_birth, gender):



    


    return [{"id": 1, "name": "John"}]


@router.post("/login")
async def login_user():
    return [{"id": 1, "name": "John"}]


@router.post("/verification/otp/email")
async def otp_verification():
    return [{"id": 1, "name": "John"}]


@router.post("/logout")
async def logout_user():
    return [{"id": 1, "name": "John"}]