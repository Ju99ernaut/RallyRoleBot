import data
import json

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class CoinMapping(BaseModel):
    guildId: str
    coinKind: str


router = APIRouter()


@router.get("/mappings/coin/{guildId}", tags=["coin"], response_model=CoinMapping)
async def read_mapping(guildId: str):
    return {"guild_id": guildId, "coinKind": data.get_default_coin(guildId)}


@router.post("/mappings/coin", tags=["coin"], response_model=CoinMapping)
async def add_mapping(mapping: CoinMapping):
    data.add_default_coin(mapping[GUILD_ID_KEY], mapping[COIN_KIND_KEY])
    return {
        "guild_id": mapping[GUILD_ID_KEY],
        "coinKind": data.get_default_coin(mapping[GUILD_ID_KEY]),
    }
