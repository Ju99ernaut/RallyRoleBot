from typing import Optional
from pydantic import BaseModel


class ChannelMapping(BaseModel):
    id: Optional[int] = None
    guildId: Optional[str] = None
    coinKind: str
    requiredBalance: str
    channel: str


class RoleMapping(BaseModel):
    id: Optional[int] = None
    guildId: Optional[str] = None
    coinKind: str
    requiredBalance: str
    roleName: str


class CoinMapping(BaseModel):
    guildId: Optional[str] = None
    coinKind: str


class PrefixMapping(BaseModel):
    guildId: Optional[str] = None
    prefix: str
    
    
class Command(BaseModel):
    name: str
    description: str