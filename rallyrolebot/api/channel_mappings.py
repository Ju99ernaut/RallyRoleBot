import data

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class ChannelMapping(BaseModel):
    id: Optional[int] = None
    guildId: Optional[str] = None
    coinKind: str
    requiredBalance: str
    channel: str


router = APIRouter()


@router.get(
    "/mappings/channels/{guildId}",
    tags=["channels"],
    response_model=List[ChannelMapping],
)
async def read_mappings(guildId: str):
    return [mappings for mappings in data.get_channel_mappings(guildId)]


@router.post(
    "/mappings/channels", tags=["channels"], response_model=List[ChannelMapping]
)
async def add_mappings(mapping: ChannelMapping, guildId: str):
    data.add_channel_coin_mapping(
        guildId,
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[CHANNEL_NAME_KEY],
    )
    return [mappings for mappings in data.get_channel_mappings(guildId)]


@router.delete(
    "/mappings/channels", tags=["channels"], response_model=List[ChannelMapping]
)
async def delete_mappings(mapping: ChannelMapping, guildId: str):
    data.remove_channel_mapping(
        guildId,
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[CHANNEL_NAME_KEY],
    )
    return [mappings for mappings in data.get_channel_mappings(guildId)]
