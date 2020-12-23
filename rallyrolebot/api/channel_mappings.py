import data

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class ChannelMapping(BaseModel):
    id: Optional[int] = None
    guildId: str
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
    channels = []
    for mappings in data.get_channel_mappings(guildId):
        roles.append(mappings)
    return channels


@router.post(
    "/mappings/channels", tags=["channels"], response_model=List[ChannelMapping]
)
async def add_mappings(mapping: ChannelMapping):
    data.add_channel_coin_mapping(
        mapping[GUILD_ID_KEY],
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[CHANNEL_NAME_KEY],
    )
    channels = []
    for mappings in data.get_channel_mappings(mapping[GUILD_ID_KEY]):
        roles.append(mappings)
    return channels


@router.delete(
    "/mappings/channels", tags=["channels"], response_model=List[ChannelMapping]
)
async def delete_mappings(mapping: ChannelMapping):
    data.remove_channel_mapping(
        mapping[GUILD_ID_KEY],
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[CHANNEL_NAME_KEY],
    )
    channels = []
    for mappings in data.get_channel_mappings(mapping[GUILD_ID_KEY]):
        roles.append(mappings)
    return channels
