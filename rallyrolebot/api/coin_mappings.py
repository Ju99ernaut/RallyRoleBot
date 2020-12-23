import data

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class CoinMapping(BaseModel):
    guildId: Optional[str] = None
    coinKind: str


router = APIRouter()


@router.get("/mappings/coin/{guildId}", tags=["coin"], response_model=CoinMapping)
async def read_mapping(guildId: str):
    return {"guild_id": guildId, "coinKind": data.get_default_coin(guildId)}


@router.post("/mappings/coin", tags=["coin"], response_model=CoinMapping)
async def add_mapping(mapping: CoinMapping, guildId: str):
    data.add_default_coin(guildId, mapping[COIN_KIND_KEY])
    return {
        "guild_id": mapping[GUILD_ID_KEY],
        "coinKind": data.get_default_coin(guildId),
    }
