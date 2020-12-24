import data

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .dependencies import owner_or_admin

from constants import *


class PrefixMapping(BaseModel):
    guildId: Optional[str] = None
    prefix: str


router = APIRouter(
    prefix="/mappings/prefix",
    tags=["prefix"],
    dependencies=[Depends(owner_or_admin)],
)


@router.get("/{guildId}", response_model=PrefixMapping)
async def read_mapping(guildId: str):
    return {"guildId": guildId, "prefix": data.get_prefix(guildId)}


@router.post("/", response_model=PrefixMapping)
async def add_mapping(mapping: PrefixMapping, guildId: str):
    data.add_prefix_mapping(guildId, mapping[PREFIX_KEY])
    return {
        "guildId": guildId,
        "prefix": data.get_prefix(guildId),
    }
