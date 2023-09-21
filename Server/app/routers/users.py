from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.models import userDto
from app.crud import userCurd
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.service.user import (
    get_password_hash,
    authenticate_user,
    get_current_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    oauth2_scheme,
)
from app.entities import organizations, roles, users
from app.db import engine
from sqlalchemy import select
from app.util import is_valid_password

organizations.Base.metadata.create_all(bind=engine)
roles.Base.metadata.create_all(bind=engine)
users.Base.metadata.create_all(bind=engine)

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/users/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: userDto.User = Depends(get_current_user)):
    del current_user.password
    current_user.role
    current_user.organization
    return current_user


@router.get(
    "/users", dependencies=[Depends(oauth2_scheme)], response_model=Page[userDto.User]
)
def get_users(db: Session = Depends(get_db)):
    return paginate(
        db,
        select(users.User).order_by(users.User.createdAt.desc()),
    )


@router.post("/users", dependencies=[Depends(oauth2_scheme)])
def create_user(user: userDto.UserCreate, db: Session = Depends(get_db)):
    if userCurd.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="该用户名已存在",
        )
    user.password = get_password_hash(user.password)
    userCurd.create_user(db, user)
    del user.password
    return user

@router.put("/users/me", dependencies=[Depends(oauth2_scheme)])
def change_password(
    user_update: userDto.UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: userDto.User = Depends(get_current_user),
):
    user = authenticate_user(current_user.username, user_update.old_password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not is_valid_password(user_update.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不符合要求",
        )
    user.password = get_password_hash(user_update.new_password)
    userCurd.update_user_password(db, user)
    return {"data": "success"}

@router.put("/users/{user_id}", dependencies=[Depends(oauth2_scheme)])
def update_users(user_id: int, user: userDto.UserUpdate, db: Session = Depends(get_db)):
    update_user = userCurd.update_user(db, user_id, user)
    return {"data": update_user}



