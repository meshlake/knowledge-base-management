from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from starlette.responses import Response
from app.service.casbinEnforcer import authorize
from .routers import (
    users,
    organization,
    auth,
    roles,
    knowledge_base,
    chatbot,
    file_manage,
    review,
    application,
    wechat_bot,
)
from fastapi_pagination import add_pagination
from fastapi.routing import APIRoute
from app.service import user
from .dependencies import get_db

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organization.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(knowledge_base.router)
app.include_router(chatbot.router)
app.include_router(application.router)
app.include_router(file_manage.router)
app.include_router(review.router)
app.include_router(wechat_bot.router)


add_pagination(app)

async def startup():
    db = next(get_db())
    await user.create_default_user(db)
    db.close()

# 注册回调函数
app.add_event_handler("startup", startup)

# 路由白名单
whitelist = [
    "/users/login"
]

# 获取所有路由
all_routes = app.routes

# 遍历所有路由，将非 APIRoute 类型的路由加入白名单
for route in all_routes:
    if not isinstance(route, APIRoute):
        whitelist.append(route.path)

# 注册权限验证中间件
@app.middleware("http")
async def add_auth_middleware(request: Request, call_next):
    # 调用自定义中间件并传递额外参数
    try: 
        response = await authorize(request, call_next, whitelist=whitelist)
        return response
    except HTTPException as e:
        return Response(status_code=e.status_code, content=e.detail)
@app.get("/")
def root():
    return {"message": "Hello Doc"}