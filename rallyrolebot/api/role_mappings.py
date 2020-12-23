import data

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from constants import *


class RoleMapping(BaseModel):
    id: Optional[int] = None
    guildId: str
    coinKind: str
    requiredBalance: str
    roleName: str


router = APIRouter()


@router.get(
    "/mappings/roles/{guildId}", tags=["roles"], response_model=List[RoleMapping]
)
async def read_mappings(guildId: str):
    return [mappings for mappings in data.get_role_mappings(guildId)]


@router.post("/mappings/roles", tags=["roles"], response_model=List[RoleMapping])
async def add_mapping(mapping: RoleMapping):
    data.add_role_coin_mapping(
        mapping[GUILD_ID_KEY],
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[ROLE_NAME_KEY],
    )
    return [mappings for mappings in data.get_role_mappings(mapping[GUILD_ID_KEY])]


@router.delete("/mappings/roles", tags=["roles"], response_model=List[RoleMapping])
async def delete_mapping(mapping: RoleMapping):
    data.remove_role_mapping(
        mapping[GUILD_ID_KEY],
        mapping[COIN_KIND_KEY],
        mapping[REQUIRED_BALANCE_KEY],
        mapping[ROLE_NAME_KEY],
    )
    return [mappings for mappings in data.get_role_mappings(mapping[GUILD_ID_KEY])]
