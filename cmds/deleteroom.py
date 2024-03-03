import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes a single room from the database
@commands.hybrid_command(name="deleteroom", description="Delete a room by its ID")
async def deleteroom(ctx, room_id: str):
  # Retrieve room information from the database based on room_id
  room = database.testrooms.find_one({"roomid": room_id})
  if not room:
    await ctx.reply("Error: Room not found! Double check your room ID!", ephemeral=True)
    # Check if the room belongs to the user
    # if not, then check for maintainer
  if ctx.author.id == room["author"] or permissions.is_maintainer(ctx):
    confirm = await database.confirm_embed(confirm_text=f"This will delete the room {room['displayname']} permenantly, are you sure you want to do this?", title="Confirm Room Deletion", action="delete_room", channel=ctx.channel, id=room_id)
    embed = confirm[0]
    view = confirm[1]
    await ctx.reply(embed=embed, view=view, ephemeral=True)
  else:
    await ctx.reply("Error: You do not have permission to delete this room!", ephemeral=True)


@deleteroom.autocomplete('room_id')
async def autocomplete_room_id_deletion(interaction: discord.Interaction, current: str):
  #checks if author is maintainer, finds every room
  if database.check_permissions(interaction.user.id)[0]:
    room_ids_query = database.testrooms.find(
  {
  "roomid": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "roomid": 1, 
  "_id": 0
  }
  )
    room_ids = [room["roomid"] for room in room_ids_query.limit(25)]
    return [app_commands.Choice(name=room_id, value=room_id) for room_id in room_ids]
  else:
    room_ids_query = database.testrooms.find(
  {
  "author": interaction.user.id,
  "roomid": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "roomid": 1, 
  "_id": 0
  }
  )
    room_ids = [room["roomid"] for room in room_ids_query.limit(25)]
    return [app_commands.Choice(name=room_id, value=room_id) for room_id in room_ids]
  

async def setup(bot):
  bot.add_command(deleteroom)