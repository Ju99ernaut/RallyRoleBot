from fastapi import Header, HTTPException

import requests

from constants import *


def returnReqError(url, result):
    print("Request error!")
    print(f"Url: {url}")
    print(f"Status Code: {result.status_code}")
    print(f"JSON result type: {type(result.json())}")
    print(result.json())


def get_user(token):
    url = DISCORD_API_URL + "/users/@me"
    headers = {"authorization": authorization}
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        returnReqError(url, result)
        return None
    return result.json()


def owner_or_admin_guilds(token):
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
    guilds = owner_or_admin_guilds(authorization, guildId)
    if not guilds or guildId in guilds:
        raise HTTPException(status_code=400, detail="you cannot modify this record")