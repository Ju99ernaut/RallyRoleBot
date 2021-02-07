import data

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

    return {"guildId": guildId, "bot_name": bot_instance[BOT_NAME_KEY], 'name_timeout': int(bool(bot_instance[NAME_TIMEOUT_KEY]))}


@router.post("/", response_model=BotNameMapping)
async def add_mapping(mapping: BotNameMapping, guildId: str):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        raise HTTPException(status_code=404, detail="Bot config not found")

    if mapping.bot_name is not None and not bot_instance[NAME_TIMEOUT_KEY]:
        data.set_bot_name(guildId, mapping.bot_name)
        bot_name = mapping.bot_name
    else:
        bot_name = bot_instance[NAME_KEY]

    return {"guildId": guildId, "bot_name": bot_name, 'name_timeout': int(bool(bot_instance[NAME_TIMEOUT_KEY]))}
