import data
import json

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class PrefixMapping(BaseModel):
    guildId: str
    prefix: str


router = APIRouter()


@router.get(
    "/mappings/prefix/{guildId}", tags=["prefix"], response_model=PrefixMapping
)
async def read_mapping(guildId: str):
    return {"guildId": guildId, "prefix": data.get_prefix(guildId)}


@router.post("/mappings/prefix", tags=["prefix"], response_model=PrefixMapping)
async def add_mapping(mapping: PrefixMapping):
    data.add_prefix_mapping(mapping[GUILD_ID_KEY], mapping[PREFIX_KEY])
    return {
        "guild_id": mapping[GUILD_ID_KEY],
        "prefix": data.get_prefix(mapping[GUILD_ID_KEY]),
    }
