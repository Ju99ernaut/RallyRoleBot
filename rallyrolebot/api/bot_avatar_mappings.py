import data
import re
import base64
import time
from cogs import update_cog

from fastapi import APIRouter, Depends, HTTPException
from .dependencies import owner_or_admin
from .models import BotAvatarMapping
from constants import *

import config
config.parse_args()


router = APIRouter(
    prefix="/mappings/bot_avatar",
    tags=["bot_avatar"],
    dependencies=[Depends(owner_or_admin)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{guildId}", response_model=BotAvatarMapping)
async def read_mapping(guildId: str):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        return {"bot_avatar": DEFAULT_BOT_AVATAR_URL, "guildId": guildId}

    avatar = bot_instance[BOT_AVATAR_KEY]
    # set avatar in db to current bot avatar_url if name is empty
    if not avatar:
        bot_object = update_cog.running_bots[bot_instance[BOT_ID_KEY]]['bot']
        avatar = bot_object.user.avatar_url
        data.set_bot_avatar(guildId, str(bot_object.user.avatar_url))

    return {"bot_avatar": avatar, "avatar_timeout": int(bool(bot_instance[AVATAR_TIMEOUT_KEY])), "guildId": guildId}


@router.post("", response_model=BotAvatarMapping)
async def add_mapping(mapping: BotAvatarMapping, guildId: str):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        raise HTTPException(status_code=404, detail="Bot config not found")

    # avatar timout
    if bot_instance[AVATAR_TIMEOUT_KEY] and int(bot_instance[AVATAR_TIMEOUT_KEY]) <= time.time():
        data.set_avatar_timout(bot_instance[GUILD_ID_KEY], 0)
        bot_instance[AVATAR_TIMEOUT_KEY] = 0

    bot_object = update_cog.running_bots[bot_instance[BOT_ID_KEY]]['bot']
    if mapping.bot_avatar is not None and not bot_instance[AVATAR_TIMEOUT_KEY]:
        # get image from base64
        ext, image_data = re.findall('/(.*);base64,(.*)', mapping.bot_avatar)[0]
        new_avatar = base64.decodebytes(image_data.encode('utf-8'))

        error = await update_cog.update_avatar(bot_instance, new_avatar)

        if error:
            raise HTTPException(status_code=500, detail="Error changing bot avatar")

    return {"bot_avatar": str(bot_object.user.avatar_url), 'guildId': guildId, 'avatar_timeout': int(bool(bot_instance[AVATAR_TIMEOUT_KEY]))}
