import os
import threading
from typing import List

import asyncio
import uvicorn
import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api import channel_mappings, role_mappings, prefix_mappings, coin_mappings
from api.models import Command

import config
import data
import json

from cogs import *
from constants import *


config.parse_args()
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
default_prefix = config.CONFIG.command_prefix


def prefix(bot, ctx):
    guildId = ctx.guild.id
    return data.get_prefix(guildId) or default_prefix


bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.add_cog(role_cog.RoleCommands(bot))
bot.add_cog(channel_cog.ChannelCommands(bot))
bot.add_cog(rally_cog.RallyCommands(bot))
bot.add_cog(defaults_cog.DefaultsCommands(bot))
bot.add_cog(update_cog.UpdateTask(bot))


app = FastAPI(
    title="Rally Discord Bot API",
    description="API for communicating with the Rally Role Bot for Discord",
    version="1.0.0",
    openapi_tags=API_TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(channel_mappings.router)
app.include_router(role_mappings.router)
app.include_router(prefix_mappings.router)
app.include_router(coin_mappings.router)


@app.on_event("startup")
async def startup_event():
    asyncio.get_event_loop().create_task(bot.start(config.CONFIG.secret_token))


@app.get("/")
async def root():
    return {"bot": str(bot.user), "docs": "/docs or /redoc"}


@app.get("/commands", tags=["commands"], response_model=List[Command])
async def read_commands():
    commands = []
    for command in bot.commands:
        commands.append({"name": command.name, "description": command.help})
    return commands


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT")) or 5000)
