import json
import sys
import traceback
import threading
import time

import discord
from discord.ext import commands, tasks
from discord.utils import get

from constants import *

import cogs.role_cog
import cogs.rally_cog
import cogs.defaults_cog
import cogs.channel_cog
import aiohttp

import config
import asyncio
import errors
import data
import rally_api
import validation

from utils import pretty_print

main_bot = None
running_bots = {}
running_bot_instances = []


async def grant_deny_channel_to_member(channel_mapping, member, balances):
    """
    Determine if the rally_id and balance for a channel is still valid for a particular member
    Update status in database.

    Parameters
    __________

      channel_mapping  (list) - list of information for the channel mapped to the member
      member (discord.Member) - The discord member to check
      balances (list)  - The amount of coin allocated to this member per coin

    """

    print("Checking channel")
    rally_id = data.get_rally_id(member.id)
    if rally_id is None or balances is None:
        return
    matched_channels = [
        channel
        for channel in member.guild.channels
        if channel.name == channel_mapping[data.CHANNEL_NAME_KEY]
    ]
    if len(matched_channels) == 0:
        return
    channel_to_assign = matched_channels[0]
    if channel_to_assign is not None:
        if (
            rally_api.find_balance_of_coin(
                channel_mapping[data.COIN_KIND_KEY], balances
            )
            >= channel_mapping[data.REQUIRED_BALANCE_KEY]
        ):
            perms = channel_to_assign.overwrites_for(member)
            perms.send_messages = True
            perms.read_messages = True
            perms.read_message_history = True
            await channel_to_assign.set_permissions(member, overwrite=perms)
            print("Assigned channel to member")
        else:
            perms = channel_to_assign.overwrites_for(member)
            perms.send_messages = False
            perms.read_messages = False
            perms.read_message_history = False
            await channel_to_assign.set_permissions(member, overwrite=perms)
            print("Removed channel to member")
    else:
        print("Channel not found")


async def grant_deny_role_to_member(role_mapping, member, balances):
    """
    Determine if the rally_id and balance for a role is still valid for a particular member
    Update status in database.

    Parameters
    __________

      channel_mapping (list) - list of information for the channel mapped to the member
      member (discord.Member) - The discord member to check
      balances (list)  - The amount allocated to this member per coin

    """

    rally_id = data.get_rally_id(member.id)
    if rally_id is None or balances is None:
        return
    role_to_assign = get(member.guild.roles, name=role_mapping[data.ROLE_NAME_KEY])
    if (
        rally_api.find_balance_of_coin(role_mapping[data.COIN_KIND_KEY], balances)
        >= role_mapping[data.REQUIRED_BALANCE_KEY]
    ):
        if role_to_assign is not None:
            await member.add_roles(role_to_assign)
            print("Assigned role to member")
        else:
            print("Can't find role")
            print(role_mapping["role"])
    else:
        if role_to_assign in member.roles:
            await member.remove_roles(role_to_assign)
            print("Removed role to member")


async def force_update(bot, ctx):
    await bot.get_cog("UpdateTask").force_update(ctx)


async def update_activity(bot_instance, new_activity_type, new_activity_text):
    error = False
    if new_activity_type and new_activity_text:
        if new_activity_type == 'playing':
            activity_type = discord.ActivityType.playing
        elif new_activity_type == 'listening':
            activity_type = discord.ActivityType.listening
        elif new_activity_type == 'competing':
            activity_type = discord.ActivityType.competing
        elif new_activity_type == 'watching':
            activity_type = discord.ActivityType.watching
        else:
            error = True
            return error

        current_activity = running_bots[bot_instance[BOT_ID_KEY]]['activity']
        bot_object = running_bots[bot_instance[BOT_ID_KEY]]['bot']

        try:
            if not current_activity or (current_activity and current_activity.type != new_activity_text) or \
                    (current_activity and repr(current_activity.name) != repr(new_activity_text)):
                # check that current_activity isnt duplicate of new activity
                new_activity = discord.Activity(type=activity_type, name=new_activity_text)
                running_bots[bot_instance[BOT_ID_KEY]]['activity'] = new_activity
                await bot_object.change_presence(status=discord.Status.online, activity=new_activity)
                data.set_activity(bot_instance[GUILD_ID_KEY], new_activity_type, new_activity_text)
        except:
            error = True

    return error


async def update_avatar(bot_instance, new_avatar=None):
    if new_avatar is None:
        async with aiohttp.ClientSession() as session:
            async with session.get(DEFAULT_BOT_AVATAR_URL) as response:
                new_avatar = await response.read()

    error = False
    # avatar change
    try:
        bot_object = running_bots[bot_instance[BOT_ID_KEY]]['bot']
        await bot_object.user.edit(avatar=new_avatar)
        data.set_bot_avatar(bot_instance[GUILD_ID_KEY], str(bot_object.user.avatar_url))
    except discord.HTTPException:
        # user is editing avatar too many times, set 1h timeout
        timout = round(time.time() + 3600)
        data.set_avatar_timout(bot_instance[GUILD_ID_KEY], timout)
        bot_instance[AVATAR_TIMEOUT_KEY] = timout
    except Exception as e:
        print(e)
        error = True

    return error


class UpdateTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_lock = threading.Lock()

    @staticmethod
    async def start_bot_instance(bot_instance):
        config.parse_args()
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        default_prefix = config.CONFIG.command_prefix

        def prefix(bot, ctx):
            try:
                guildId = ctx.guild.id
                return data.get_prefix(guildId) or default_prefix
            except:
                return default_prefix

        bot = commands.Bot(command_prefix=prefix, intents=intents)
        bot.add_cog(cogs.role_cog.RoleCommands(bot))
        bot.add_cog(cogs.channel_cog.ChannelCommands(bot))
        bot.add_cog(cogs.rally_cog.RallyCommands(bot))
        bot.add_cog(cogs.defaults_cog.DefaultsCommands(bot))
        bot.add_cog(cogs.update_cog.UpdateTask(bot))

        for command in bot.commands:
            data.add_command(command.name, command.help)

        try:
            await bot.start(bot_instance)

        finally:
            if not bot.is_closed():
                await bot.close()

        running_bot_instances.remove(bot_instance[BOT_TOKEN_KEY])

    async def run_bot_instances(self):
        all_bot_instances = data.get_all_bot_instances()
        if all_bot_instances:
            for instance in all_bot_instances:
                running_bot_instances.append(instance[BOT_TOKEN_KEY])
                asyncio.create_task(self.start_bot_instance(instance[BOT_TOKEN_KEY]))

    @commands.Cog.listener()
    async def on_ready(self):
        running_bots[self.bot.user.id] = {
            'bot': self.bot,
            'token': self.bot.http.token,
            'activity': None
        }

        # for instances
        if config.CONFIG.secret_token != self.bot.http.token:
            bot_instance = data.get_bot_instance_token(self.bot.http.token)

            if bot_instance[BOT_ACTIVITY_TEXT_KEY]:
                await update_activity(bot_instance, bot_instance[BOT_ACTIVITY_TYPE_KEY], bot_instance[BOT_ACTIVITY_TEXT_KEY])

            # set bot id
            data.set_bot_id(self.bot.user.id, self.bot.http.token)
            # set bot name
            data.set_bot_name(bot_instance[GUILD_ID_KEY], self.bot.user.name)

        # for the main bot
        if not running_bot_instances:
            global main_bot
            main_bot = self.bot
            self.update.start()
            asyncio.create_task(self.run_bot_instances())

        print("We have logged in as {0.user}".format(self.bot))

    @errors.standard_error_handler
    async def cog_command_error(self, ctx, error):
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    @commands.command(name="update", help="Force an immediate update")
    @validation.owner_or_permissions(administrator=True)
    async def force_update(self, ctx):
        self.update.restart()
        await ctx.send("Updating!")

    @tasks.loop(seconds=UPDATE_WAIT_TIME)
    async def update(self):
        await self.bot.wait_until_ready()
        with self.update_lock:

            print("Updating roles")
            guilds = self.bot.guilds
            guild_count = 0
            member_count = 0
            mapping_count = 0

            for guild in guilds:

                guild_count += 1
                await guild.chunk()

                role_mappings = list(data.get_role_mappings(guild.id))
                channel_mappings = list(data.get_channel_mappings(guild.id))
                mapping_count += len(role_mappings) + len(channel_mappings)

                for member in guild.members:
                    member_count += 1
                    rally_id = data.get_rally_id(member.id)
                    if rally_id:
                        balances = rally_api.get_balances(rally_id)
                        for role_mapping in role_mappings:
                            print(role_mapping)
                            await grant_deny_role_to_member(
                                role_mapping, member, balances
                            )
                        for channel_mapping in channel_mappings:
                            await grant_deny_channel_to_member(
                                channel_mapping, member, balances
                            )

            print(
                "Done! Checked "
                + str(guild_count)
                + " guilds. "
                + str(mapping_count)
                + " mappings. "
                + str(member_count)
                + " members."
            )

    @commands.command(
        name='change_rally_id',
        help="updates your wallet balance / roles immediately"
    )
    @commands.guild_only()
    async def set_rally_id(self, ctx):
        member = ctx.author

        with self.update_lock:
            for guild in self.bot.guilds:
                await guild.chunk()

                if not member in guild.members:
                    continue

                role_mappings = list(data.get_role_mappings(guild.id))
                channel_mappings = list(data.get_channel_mappings(guild.id))

                rally_id = data.get_rally_id(member.id)
                if rally_id:
                    balances = rally_api.get_balances(rally_id)
                    for role_mapping in role_mappings:
                        try:
                            await grant_deny_role_to_member(
                                role_mapping, member, balances
                            )
                        except discord.HTTPException:
                            raise errors.RequestError("network error, try again later")
                        except:
                            # Forbidden, NotFound or Invalid Argument exceptions only called when code
                            # or bot is wrongly synced / setup
                            raise errors.FatalError("bot is setup wrong, call admin")
                    for channel_mapping in channel_mappings:
                        try:
                            await grant_deny_channel_to_member(
                                channel_mapping, member, balances
                            )
                        except discord.HTTPException:
                            raise errors.RequestError("network error, try again later")
                        except:
                            # Forbidden, NotFound or Invalid Argument exceptions only called when code
                            # or bot is wrongly synced / setup
                            raise errors.FatalError("bot is setup wrong, call admin")

            await pretty_print(
                ctx,
                "Command completed successfully!",
                title="Success",
                color=SUCCESS_COLOR,
            )
