import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


# Shows what a room/item will look like
# Can also preview player info, but only as a maintainer
@commands.hybrid_command(name="viewall", description="Shows all the keys and rooms you've created")
async def viewall(ctx):
  if not permissions.is_assistant_or_maintainer(ctx):
    await ctx.reply("You don't have permission to use this command")
    return
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  #shows all rooms
  all_rooms = database.rooms.find({"author": ctx.author.id})
  for room in all_rooms:
    await ctx.send(f"**Room {room['id']} - {room['displayname']}\n{room['description']}**", ephemeral=True)
  #shows all keys
  all_keys = database.keys.find({"author": ctx.author.id})
  for key in all_keys:
    await ctx.send(f"**Key {key['id']} - {key['displayname']}\n{key['description']}**", ephemeral=True)

async def setup(bot):
  bot.add_command(viewall)