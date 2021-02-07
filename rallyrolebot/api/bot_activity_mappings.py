import data
import re
import base64
import os

import config
config.parse_args()

from fastapi import APIRouter, Depends, HTTPException
from .dependencies import owner_or_admin
from .models import BotActivityMapping
from constants import *


router = APIRouter(
    prefix="/mappings/bot_activity",
    tags=["bot_avatar"],
    dependencies=[Depends(owner_or_admin)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{guildId}", response_model=BotActivityMapping)
async def read_mapping(guildId):
    bot_instance = data.get_bot_instance(guildId)
    if not bot_instance:
        return {}

    activity_text = bot_instance[BOT_ACTIVITY_TEXT_KEY]
    activity_type = bot_instance[BOT_ACTIVITY_TYPE_KEY]

    return {"activity_text": activity_text, "activity_type": activity_type}


@router.post("", response_model=BotActivityMapping)
async def add_mapping(mapping: BotActivityMapping, guildId):
    bot_instance = data.get_bot_instance(guildId)

    if not bot_instance:
        raise HTTPException(status_code=404, detail="Bot config not found")

    if mapping.activity_type is not None and mapping.activity_text is not None:
        data.set_activity(guildId, mapping.activity_type, mapping.activity_text)

    return {"success": 1}
