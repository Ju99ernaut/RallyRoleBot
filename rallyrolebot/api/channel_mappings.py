import data

from typing import List
from fastapi import APIRouter, Depends
from .dependencies import owner_or_admin
from .models import ChannelMapping

import config
config.parse_args()

router = APIRouter(
    prefix="/mappings/channels",
    tags=["channels"],
    dependencies=[Depends(owner_or_admin)],
)


@router.get("/{guildId}", response_model=List[ChannelMapping])
async def read_mappings(guildId: str):
    return [mappings for mappings in data.get_channel_mappings(guildId)]


@router.post("", response_model=List[ChannelMapping])
async def add_mappings(mapping: ChannelMapping, guildId: str):
    data.add_channel_coin_mapping(
        guildId,
        mapping.coinKind,
        mapping.requiredBalance,
        mapping.channel,
    )
    return [mappings for mappings in data.get_channel_mappings(guildId)]


@router.delete(
    "",
    response_model=List[ChannelMapping],
)
async def delete_mappings(mapping: ChannelMapping, guildId: str):
    data.remove_channel_mapping(
        guildId,
        mapping.coinKind,
        mapping.requiredBalance,
        mapping.channel,
    )
    return [mappings for mappings in data.get_channel_mappings(guildId)]