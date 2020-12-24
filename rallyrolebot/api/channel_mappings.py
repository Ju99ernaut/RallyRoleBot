import data

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .dependencies import owner_or_admin

from constants import *


class ChannelMapping(BaseModel):
    id: Optional[int] = None
    guildId: Optional[str] = None
    coinKind: str
    requiredBalance: str
    channel: str


router = APIRouter(
    prefix="/mappings/channels",
    tags=["channels"],
    dependencies=[Depends(owner_or_admin)],
)


@router.get("/{guildId}", response_model=List[ChannelMapping])
async def read_mappings(guildId: str):
    return [mappings for mappings in data.get_channel_mappings(guildId)]


@router.post("/", response_model=List[ChannelMapping])
async def add_mappings(mapping: ChannelMapping, guildId: str):
    data.add_channel_coin_mapping(
        guildId,
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[CHANNEL_NAME_KEY],
    )
    return [mappings for mappings in data.get_channel_mappings(guildId)]


@router.delete(
    "/",
    response_model=List[ChannelMapping],
)
async def delete_mappings(mapping: ChannelMapping, guildId: str):
    data.remove_channel_mapping(
        guildId,
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[CHANNEL_NAME_KEY],
    )
    return [mappings for mappings in data.get_channel_mappings(guildId)]
