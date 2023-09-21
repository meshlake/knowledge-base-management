import json
import logging
from fastapi import Request, Depends
from casbin_sqlalchemy_adapter import Adapter
from casbin import Enforcer
from app.db import engine
from starlette.responses import Response
from app.util import is_path_in_whitelist
from app.models import userDto
from app.service.user import get_current_user_without_depends
import os

# 创建 Casbin Adapter
adapter = Adapter(engine)

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = "../casbin.conf"
absolute_path = os.path.join(current_dir, relative_path)

# 初始化 Casbin Enforcer
enforcer = Enforcer(
    absolute_path,
    adapter,
)

# 初始化admin权限
current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = "../auth.json"
absolute_path = os.path.join(current_dir, relative_path)
with open(absolute_path, "r") as file:
    data = json.load(file)
for permission in data:
    enforcer.add_permission_for_user(
        "admin", permission["type"], permission["route"], permission["method"]
    )

# 定义权限验证中间件
async def authorize(request: Request, call_next, whitelist: list):
    # 获取当前请求的路径和方法
    path = request.url.path
    method = request.method
    # 检查请求路径是否在白名单中
    if is_path_in_whitelist(path, whitelist):
        # 调用下一个中间件或路由处理函数
        return await call_next(request)

    current_user = await get_current_user_without_depends(request)
    logging.info(f"{current_user.username} {method} {path}")
    # 获取当前用户的角色
    role = current_user.role.code

    if role == "admin":
        # 调用下一个中间件或路由处理函数
        return await call_next(request)

    # 检查权限
    if not enforcer.enforce(role, 'api', path, method):
        response = Response(status_code=403, content="Permission denied")
        return response

    response = await call_next(request)
    return response
