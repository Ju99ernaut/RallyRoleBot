import data

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .dependencies import owner_or_admin

from constants import *


class CoinMapping(BaseModel):
    guildId: Optional[str] = None
    coinKind: str


router = APIRouter(
    prefix="/mappings/coin",
    tags=["coin"],
    dependencies=[Depends(owner_or_admin)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{guildId}", response_model=CoinMapping)
async def read_mapping(guildId: str):
    coinKind = data.get_default_coin(guildId)
    if not coinKind:
        raise HTTPException(status_code=404, detail="Coin not found")
    return {"guildId": guildId, "coinKind": coinKind}


@router.post("/", response_model=CoinMapping)
async def add_mapping(mapping: CoinMapping, guildId: str):
    data.add_default_coin(guildId, mapping[COIN_KIND_KEY])
    coinKind = data.get_default_coin(guildId)
    if not coinKind:
        raise HTTPException(status_code=404, detail="Coin not found")
    return {"guildId": guildId, "coinKind": coinKind}
