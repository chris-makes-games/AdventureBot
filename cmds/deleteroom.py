import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes a single room from the database
@commands.hybrid_command(name="deleteroom", description="Delete a room by its ID")
async def deleteroom(ctx, room_id: str):
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
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
  # Retrieve room information from the database based on room_id
  room = database.rooms.find_one({"id": room_id})
  if not room:
    await ctx.reply("Error: Room not found! Double check your room ID!", ephemeral=True)
    # Check if the room belongs to the user
    # if not, then check for maintainer
  if ctx.author.id == room["author"] or permissions.is_maintainer(ctx):
    confirm = await database.confirm_embed(ctx.interaction.id, confirm_text=f"This will delete the room **{room['displayname']}** permenantly, are you sure you want to do this?\n**THIS CANNOT BE UNDONE!**", title="Confirm Room Deletion", action="delete_room", channel=ctx.channel, id=room_id)
    embed = confirm[0]
    view = confirm[1]
    await ctx.reply(embed=embed, view=view, ephemeral=True)
  else:
    await ctx.reply("Error: You do not have permission to delete this room!", ephemeral=True)


@deleteroom.autocomplete('room_id')
async def autocomplete_room_id_deletion(interaction: discord.Interaction, current: str):
  #checks if author is maintainer, finds every room
  if database.check_permissions(interaction.user.id)[0]:
    room_ids_query = database.rooms.find(
  {
  "id": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "id": 1, 
  "_id": 0
  }
  )
    room_ids = [room["id"] for room in room_ids_query.limit(25)]
    return [app_commands.Choice(name=room_id, value=room_id) for room_id in room_ids]
  else:
    #if not maintainer, shows only their rooms
    room_ids_query = database.rooms.find(
  {
  "author": interaction.user.id,
  "id": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "id": 1, 
  "_id": 0
  }
  )
    room_ids = [room["id"] for room in room_ids_query.limit(25)]
    return [app_commands.Choice(name=room_id, value=room_id) for room_id in room_ids]
  

async def setup(bot):
  bot.add_command(deleteroom)