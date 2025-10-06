from datetime import date, timedelta, timezone
from typing import Annotated
from dotenv import load_dotenv
# Supabass Auth
import os
from supabase import create_client, Client
from supabase.client import ClientOptions

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.database import get_db
from app.models import User, JournalEntry
from app.schemas import CreateUserRequest, UpdateUserRequest, UpdateUserFoodJournalRequest, JournalEntryRequest, Token, TokenData
from app.utils.security import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Object containing auth tools
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Random secret key used to sign JWT tokens
# openssl rand -hex 32
#   CUSTOM BACKEND
# SECRET_KEY = os.getenv("SECRET_KEY")
SUPA_SECRET_KEY = os.getenv("SUPABASE_JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRATION = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# SUPABASE
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_PUBLISHABLE_API_KEY")
supabase: Client = create_client(
    url,
    key,
    options=ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=10,
        schema="public",
    )
)

# Function to get current user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    credentials_exception_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})

    credentials_exception_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials, token", headers={"WWW-Authenticate": "Bearer"})
    try:
        # payload = jwt.decode(token, SUPA_SECRET_KEY, algorithms=[ALGORITHM])
        # email = payload.get("sub")
        supa_response = supabase.auth.get_user(token)
        user_email = supa_response.user.email
        if user_email is None:
            raise credentials_exception_token
        token_data = TokenData(email=user_email)
    except InvalidTokenError:
        raise credentials_exception_token
    user: User | None = db.get(User, token_data.email)
    if user is None:
        raise credentials_exception_token
    return user



@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response, db: Session = Depends(get_db)) -> Token:

    # form_data user name is email
    user: User | None = db.get(User, form_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Invalid credentials!"))
    supa_response = supabase.auth.sign_in_with_password(
        {
            "email": form_data.username,
            "password": form_data.password,
        }
    )
    response.set_cookie(
        key="refresh_token",
        value=supa_response.session.refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=3600 * 24
    )
    return Token(access_token=supa_response.session.access_token)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(new_user_request: CreateUserRequest, db: Session = Depends(get_db)) -> None:
    # password hashed and stored by Supabase Auth
    # Check if User already exists in database
    user: User | None = db.get(User, new_user_request.username)
    if user:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="User already registered")

    response = supabase.auth.sign_up(
        {
        "email": new_user_request.email,
        "password": new_user_request.password,
        "options": {
            "data": {
                "username": new_user_request.username,
                "first_name": new_user_request.first_name,
                "last_name": new_user_request.last_name,
                },
            }
        }
    )
    user: User = User(**new_user_request.model_dump(exclude_unset=True))
    
    db.add(user)
    db.commit()
    db.refresh(user)
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="User successfully signed up!")

@router.delete("/delete_user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_email(user_email: str, current_logged_in_user = Depends(supabase.auth.get_user()), db: Session = Depends(get_db)):
    user: User | None = db.get(User, user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to delete not found")

    supabase.auth.admin.delete_user(current_logged_in_user)
    supabase.auth.sign_out()
    db.delete(user)
    db.commit()

# Get endpoint to get all users
@router.get("/users")
async def get_users(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)) -> list[User]: return db.exec(select(User)).all()

# PATCH methods
@router.patch("/update_user/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(current_user: Annotated[User, Depends(get_current_user)], user_email: str, update_user_request: UpdateUserRequest ,db: Session = Depends(get_db)) -> None:
    # Updated both database data and supabase auth data
    user: User | None = db.get(User, user_email)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {user_email}")

    for k, v in update_user_request.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    
    # supa_response = supabase.auth.update_user(
    #     {
    #         "email": update_user_request.email,
    #         "data": {
    #             "username": update_user_request.username,
    #             "first_name": update_user_request.first_name,
    #             "last_name": update_user_request.last_name,
    #         }
    #     }
    # )
    db.commit()

@router.patch("/update_food_journal/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_food_journal(current_user: Annotated[User, Depends(get_current_user)], user_email: str, journal_entry_request: JournalEntryRequest, db: Session = Depends(get_db)) -> None:
    user: User | None = db.get(User, user_email)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {user_email}")

    journal_entry: JournalEntry = JournalEntry(**journal_entry_request.model_dump())
    user.food_journal.append(journal_entry)
    
    db.commit()
    db.refresh(user)



# DELETE Methods
@router.delete("/users/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: Annotated[User, Depends(get_current_user)], user_email: str, db: Session = Depends(get_db)):
    # Deletes in database
    user: User | None = db.get(User, user_email)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {user_email} not found")


    db.delete(user)
    db.commit()
    
    # Deletes in Supabase Auth database
    supa_user = supabase.auth.get_user()
    supabase.auth.admin.delete_user(supa_user.user.id)



