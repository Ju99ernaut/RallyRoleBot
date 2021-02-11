import data
import discord
import time

from cogs import update_cog
from fastapi import APIRouter, Depends, HTTPException
from .dependencies import owner_or_admin
from .models import BotNameMapping
from constants import *

import config
config.parse_args()

router = APIRouter(
    prefix="/mappings/bot_name",
    tags=["bot_name"],
    dependencies=[Depends(owner_or_admin)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{guildId}", response_model=BotNameMapping)
async def read_mapping(guildId: str):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        return {"guildId": guildId, "bot_name": "rallybot"}

    # set name in db to current bot name if name is empty
    if not bot_instance[BOT_NAME_KEY]:
        bot_object = update_cog.running_bots[bot_instance[BOT_ID_KEY]]['bot']
        bot_instance[BOT_NAME_KEY] = bot_object.user.name
        data.set_bot_name(guildId, bot_object.user.name)

    return {"guildId": guildId, "bot_name": bot_instance[BOT_NAME_KEY], 'name_timeout': int(bool(bot_instance[NAME_TIMEOUT_KEY]))}


@router.post("/", response_model=BotNameMapping)
async def add_mapping(mapping: BotNameMapping, guildId: str):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        raise HTTPException(status_code=404, detail="Bot config not found")

    # name timout
    if bot_instance[NAME_TIMEOUT_KEY] and int(bot_instance[NAME_TIMEOUT_KEY]) <= time.time():
        data.set_name_timeout(bot_instance[GUILD_ID_KEY], 0)
        bot_instance[NAME_TIMEOUT_KEY] = 0

    bot_object = update_cog.running_bots[bot_instance[BOT_ID_KEY]]['bot']

    if mapping.bot_name and not bot_instance[NAME_TIMEOUT_KEY]:
        data.set_bot_name(guildId, mapping.bot_name)

        # name change
        try:
            if mapping.bot_name != bot_object.user.name:
                await bot_object.user.edit(username=mapping.bot_name)
                data.set_bot_name(guildId, mapping.bot_name)

        except discord.HTTPException:
            # user is editing name too many times, set 1h timeout
            timout = round(time.time() + 3600)
            data.set_name_timeout(bot_instance[GUILD_ID_KEY], timout)
            bot_instance[NAME_TIMEOUT_KEY] = timout
        except:
            raise HTTPException(status_code=500, detail="Error changing bot name")

    return {"guildId": guildId, "bot_name": bot_object.user.name, 'name_timeout': int(bool(bot_instance[NAME_TIMEOUT_KEY]))}
