from fastapi import Header, HTTPException

import requests

from rally_api import returnReqError
from constants import *


def get_user(token):
    url = DISCORD_API_URL + "/users/@me"
    headers = {"authorization": authorization}
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        returnReqError(url, result)
        return None
    return result.json()


def owner_or_admin_guilds(authorization):
    url = DISCORD_API_URL + "/users/@me/guilds"
    headers = {"authorization": authorization}
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        returnReqError(url, result)
        return None
    return [
        guild["id"]
        for guild in result.json()
        if guild["owner"] or (guild["permissions"] & 0x8) == 0x8
    ]


async def owner_or_admin(guildId: str, authorization: str = Header(...)):
    # TODO minimize calls because of rate limiting
    # guilds = owner_or_admin_guilds(authorization)
    # if not guilds or not guildId in guilds:
    #    raise HTTPException(status_code=400, detail="you cannot access this record")
    pass