import os
from fastapi import APIRouter, Depends
import requests

from app.service.user import oauth2_scheme

WECHAT_BOT_SERVER = os.getenv("WECHAT_BOT_SERVER")

router = APIRouter(
    tags=["wechatBot"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


@router.get("/api/bot/list")
async def get_bot_list():
    try:
        response = requests.get(f"{WECHAT_BOT_SERVER}/api/bot/list", timeout=3000)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/bot/{id}")
async def get_bot(id: str):
    try:
        response = requests.get(f"{WECHAT_BOT_SERVER}/api/bot/{id}", timeout=3000)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@router.post("/api/bot/{id}/logout")
async def bot_logout(id: str):
    try:
        response = requests.post(f"{WECHAT_BOT_SERVER}/api/bot/{id}/logout", timeout=3000)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
