import data

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .dependencies import owner_or_admin

from constants import *


class RoleMapping(BaseModel):
    id: Optional[int] = None
    guildId: Optional[str] = None
    coinKind: str
    requiredBalance: str
    roleName: str


router = APIRouter(
    prefix="/mappings/roles",
    tags=["roles"],
    dependencies=[Depends(owner_or_admin)],
)


@router.get("/{guildId}", response_model=List[RoleMapping])
async def read_mappings(guildId: str):
    return [mappings for mappings in data.get_role_mappings(guildId)]


@router.post("/", response_model=List[RoleMapping])
async def add_mapping(mapping: RoleMapping, guildId: str):
    data.add_role_coin_mapping(
        guildId,
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[ROLE_NAME_KEY],
    )
    return [mappings for mappings in data.get_role_mappings(guildId)]


@router.delete("/", response_model=List[RoleMapping])
async def delete_mapping(mapping: RoleMapping, guildId: str):
    data.remove_role_mapping(
        guildId,
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[ROLE_NAME_KEY],
    )
    return [mappings for mappings in data.get_role_mappings(guildId)]
