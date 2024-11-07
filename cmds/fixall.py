import discord
from discord.ext import commands
from discord import app_commands

import database
import perms_ctx as permissions
import perms_interactions as perms


from adventure import Adventure
from room import Room
from key import Key

import re

#creates room object for each room in adventure to fix all rooms with bad attributes
@commands.hybrid_command(name="fixall", description="entries in the database")
@app_commands.describe(
type="Select an type")
async def fixall(ctx, type):
  #user must be maintainer
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
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
  if type == "Adventures":
    all_adventures = database.get_adventures()
    for adventure in all_adventures:
      print(f"fixing adventure... {adventure['name']}")
      new_adventure = Adventure.from_dict(adventure)
      database.update_adventure(new_adventure.__dict__)
      print("adventure fixed!")
    await ctx.reply(f"All adventures fixed!", ephemeral=True)
  elif type == "Rooms":
    all_rooms = database.get_all_rooms()
    for room in all_rooms:
      print(f"fixing room {room['id']}...")
      new_room = Room.from_dict(room)
      database.update_room(new_room.__dict__)
      print(f"updated room {room['id']}!")
    await ctx.reply("All rooms fixed!", ephemeral=True)
  elif type == "Keys":
    all_keys = database.get_all_keys()
    for key in all_keys:
      print(f"fixing key {key['id']}...")
      new_key = Key.from_dict(key)
      database.update_room(new_key.__dict__)
      print(f"updated key {key['id']}!")
    await ctx.reply("All keys fixed!", ephemeral=True)

@fixall.autocomplete("type")
async def autocomplete_fixall(interaction: discord.Interaction, current: str):
  all_commands = ["Adventures", "Rooms", "Keys"]
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(fixall)