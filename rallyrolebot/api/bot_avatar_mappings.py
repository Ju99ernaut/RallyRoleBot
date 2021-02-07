import data
import re
import base64
import os

import config
config.parse_args()

from fastapi import APIRouter, Depends, HTTPException
from .dependencies import owner_or_admin
from .models import BotAvatarMapping
from constants import *


router = APIRouter(
    prefix="/mappings/bot_avatar",
    tags=["bot_avatar"],
    dependencies=[Depends(owner_or_admin)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{guildId}", response_model=BotAvatarMapping)
async def read_mapping(guildId):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        return {"bot_avatar": DEFAULT_BOT_AVATAR_URL, "guildId": guildId}

    avatar = bot_instance[BOT_AVATAR_KEY]

    return {"bot_avatar": avatar, "avatar_timeout": int(bool(bot_instance[AVATAR_TIMEOUT_KEY])), "guildId": guildId}


@router.post("", response_model=BotAvatarMapping)
async def add_mapping(mapping: BotAvatarMapping, guildId):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        raise HTTPException(status_code=404, detail="Bot config not found")

    if mapping.bot_avatar is not None and not bot_instance[AVATAR_TIMEOUT_KEY]:
        ext, image_data = re.findall('/(.*);base64,(.*)', mapping.bot_avatar)[0]
        file_path = os.path.abspath(f'tmp/{guildId}_bot_avatar.{ext}')

        if not os.path.exists(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))

        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'xb') as f:
            f.write(base64.decodebytes(image_data.encode('utf-8')))

        file_url = f"file://{file_path}"
        data.set_bot_avatar(guildId, file_url)

    return {"bot_avatar": "", 'guildId': guildId, 'avatar_timeout': int(bool(bot_instance[AVATAR_TIMEOUT_KEY]))}
