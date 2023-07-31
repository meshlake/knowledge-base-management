from typing import Union
from fastapi import Depends, HTTPException, status, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.crud import userCurd
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.dependencies import get_db
from app.models import userDto, organizationDto, roleDto
from .organization import create_organization
from .role import create_role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, password_in_db):
    return pwd_context.verify(plain_password, password_in_db)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session):
    user = userCurd.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


SECRET_KEY = "bde82d3e5c28299a78cefbf291d683963295ea549da507fcbe31ec9800894317"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7200


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode.update({"app_id": "doc search"})
    to_encode.update({"iss": "Middle Platform"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = userDto.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = userCurd.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: userDto.User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_without_depends(request: Request):
    token = request.headers.get("Authorization").split(" ")[1]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = userDto.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    db = next(get_db())
    user: userDto.User = userCurd.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def create_default_user(db: Session):
    admin = userCurd.get_user_by_username(db, "admin")
    if not admin:
        organization = organizationDto.OrganizationCreate(name="超级管理员组织", code="Admin")
        db_organization = create_organization(db=db, organizationcreate=organization)
        role = roleDto.RoleCreate(name="超级管理员", code="admin", description="超级管理员")
        db_role = create_role(db=db, role=role)
        user = userDto.UserCreate(
            username="admin",
            password=get_password_hash("admin@2023"),
            email="",
            nickname="超级管理员",
            phone_number="",
            organization_id=db_organization.id,
            role_id=db_role.id,
        )
        userCurd.create_user(db=db, usercreate=user)
