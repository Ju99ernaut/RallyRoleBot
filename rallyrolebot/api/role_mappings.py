import data

from typing import List
from fastapi import APIRouter, Depends
from .dependencies import owner_or_admin
from .models import RoleMapping

import config
config.parse_args()

router = APIRouter(
    prefix="/mappings/roles",
    tags=["roles"],
    dependencies=[Depends(owner_or_admin)],
)


@router.get("/{guildId}", response_model=List[RoleMapping])
async def read_mappings(guildId: str):
    return [mappings for mappings in data.get_role_mappings(guildId)]


@router.post("", response_model=List[RoleMapping])
async def add_mapping(mapping: RoleMapping, guildId: str):
    data.add_role_coin_mapping(
        guildId,
        mapping.coinKind,
        mapping.requiredBalance,
        mapping.roleName,
    )
    return [mappings for mappings in data.get_role_mappings(guildId)]


@router.delete("", response_model=List[RoleMapping])
async def delete_mapping(mapping: RoleMapping, guildId: str):
    data.remove_role_mapping(
        guildId,
        mapping.coinKind,
        mapping.requiredBalance,
        mapping.roleName,
    )
    return [mappings for mappings in data.get_role_mappings(guildId)]