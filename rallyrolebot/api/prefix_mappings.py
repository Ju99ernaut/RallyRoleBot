import data

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class PrefixMapping(BaseModel):
    guildId: Optional[str] = None
    prefix: str


router = APIRouter()


@router.get("/mappings/prefix/{guildId}", tags=["prefix"], response_model=PrefixMapping)
async def read_mapping(guildId: str):
    return {"guildId": guildId, "prefix": data.get_prefix(guildId)}


@router.post("/mappings/prefix", tags=["prefix"], response_model=PrefixMapping)
async def add_mapping(mapping: PrefixMapping, guildId: str):
    data.add_prefix_mapping(guildId, mapping[PREFIX_KEY])
    return {
        "guild_id": guildId,
        "prefix": data.get_prefix(guildId),
    }
