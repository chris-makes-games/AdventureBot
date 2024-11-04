import discord
from discord.ext import commands
from discord import app_commands

import database
import perms_ctx as permissions
import perms_interactions as perms

from room import Room

import re

#creates room object for each room in adventure to fix all rooms with bad attributes
@commands.hybrid_command(name="fixall", description="Fix all rooms for adventure")
@app_commands.describe(
adventure="Select an adventure")
async def fixall(ctx, adventure):
  #user must be maintainer
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
    return
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return
  found_adventure = database.adventures.find_one({"name": adventure.lower()})
  if found_adventure:
    print(f"fixing rooms in {adventure}")
    for room_id in found_adventure["rooms"]:
      found_room = database.get_room(room_id)
      new_room = Room.from_dict(found_room)
      database.update_room(new_room.__dict__)
      print(f"updated room {room_id}!")
    await ctx.reply(f"All rooms updated for adventure {adventure}", ephemeral=True)

@fixall.autocomplete('adventure')
async def autocomplete_fixall(interaction: discord.Interaction, current: str):
  if perms.is_assistant_or_maintainer(interaction):
    adventure_query = database.adventures.find(
      {"name": {"$regex": re.escape(current), "$options": "i"}},
      {"name": 1, "author": 1, "_id": 0}
      )
  else:
    adventure_query = []
  adventure_info = [(adventure["name"].title(), adventure["author"]) for adventure in adventure_query]
  choices = [app_commands.Choice(name=f"{name.title()}", value=name.title()) for name, author in adventure_info[:25]]
  return choices

async def setup(bot):
  bot.add_command(fixall)