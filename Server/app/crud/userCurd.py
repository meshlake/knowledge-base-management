from sqlalchemy.orm import Session
from datetime import datetime

from app.entities.users import User
from app.models.userDto import UserCreate, UserUpdate


# 创建用户
def create_user(db: Session, usercreate: UserCreate):
    user = User(
        username=usercreate.username,
        email=usercreate.email,
        password=usercreate.password,
        organization_id=usercreate.organization_id,
        nickname=usercreate.nickname,
        phone_number=usercreate.phone_number,
        disabled=False,
        role_id=usercreate.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 获取用户
def get_user(db: Session, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    return user


# 获取用户
def get_user_by_username(db: Session, username):
    user = (
        db.query(User).filter(User.username == username, User.disabled == False).first()
    )
    return user


# 更新用户
def update_user(db: Session, user_id, data: UserUpdate):
    user = db.query(User).get(user_id)
    if user:
        user.nickname = data.nickname
        user.email = data.email
        user.phone_number = data.phone_number
        user.organization_id = data.organization_id
        user.role_id = data.role_id
        user.disabled = data.disabled
        db.commit()
    return user


# 更新用户
def update_user_password(db: Session, data):
    user = db.query(User).get(data.id)
    if user:
        user.password = data.password
        db.commit()
    return user


# 删除用户
def delete_user(db: Session, user_id):
    user = db.query(User).get(user_id)
    if user:
        db.delete(user)
        db.commit()


# 修改用户角色
def update_user_role(db: Session, user_id, role_id):
    user = db.query(User).get(user_id)
    if user:
        user.role_id = role_id
        db.commit()
    return user
