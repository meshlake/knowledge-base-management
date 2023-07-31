from sqlalchemy.orm import Session

from app.entities.roles import Role
from app.models.roleDto import RoleCreate, RoleUpdate


# 创建角色
def create_role(db: Session, role_create: RoleCreate):
    role = Role(
        name=role_create.name,
        code=role_create.code,
        description=role_create.description,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


# 获取所有角色
def get_roles(db: Session):
    roles = db.query(Role).all()
    return roles


# 获取单个角色
def get_role(db: Session, role_id):
    role = db.query(Role).filter(Role.id == role_id).first()
    return role


# 更新角色
def update_role(db: Session, role_id, role_update: RoleUpdate):
    role = get_role(db=db, role_id=role_id)
    if role:
        role.name = role_update.name
        role.description = role_update.description
        db.commit()
        db.refresh(role)
    return role


# 删除角色
def delete_role(db: Session, role_id):
    role = get_role(db=db, role_id=role_id)
    if role:
        db.delete(role)
        db.commit()
    return role
