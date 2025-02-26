import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


@commands.hybrid_command(name="connectrooms", description="Connect one room to others. Mutual for two-way connects")
async def connectrooms(ctx, room1: str, room2: str, 
            room3: str | None = None, 
            room4: str | None = None, 
            room5: str | None = None,
            mutual: bool = False):
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  found_room_1 = database.get_room(room1)
  found_room_2 = database.get_room(room2)
  found_room_3 = database.get_room(room3) if room3 else None
  found_room_4 = database.get_room(room4) if room4 else None
  found_room_5 = database.get_room(room5) if room5 else None

  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  if not found_room_1:
    await ctx.reply(f"ERROR: Room '{room1}' not found.", ephemeral=True)
    return
  if not found_room_2:
    await ctx.reply(f"ERROR: Room '{room2}' not found.", ephemeral=True)
    return

  perms_errors = []
  for room in found_room_1, found_room_2, found_room_3, found_room_4, found_room_5:
    if room and room["author"] != player["disc"] and not permissions.is_maintainer:
      perms_errors.append(f"Room '{room['displayname']}' is not yours.\n")
  if perms_errors:
    await ctx.reply(f"ERROR: You do not have permission to connect those rooms!\n{perms_errors}", ephemeral=True)
    return

  embed = discord.Embed(title="Update Connecttions", description="Review the changes below and confirm the new connections:")
  if mutual:
    found_room_1["exits"].append(found_room_2["id"])
    found_room_2["exits"].append(found_room_1["id"])
    embed.add_field(name="Mutually Connecting...", value=f"( {found_room_1['displayname']} ) <----> ( {found_room_2['displayname']} )")
  else:
    print("attempting to append room id...")
    found_room_1["exits"].append(found_room_2["id"])
    print(found_room_1["exits"])
    embed.add_field(name="Connecting...", value=f"( {found_room_1['displayname']} ) -----> ( {found_room_2['displayname']} )")
  if found_room_3:
    if mutual:
      found_room_1["exits"].append(found_room_3["id"])
      found_room_3["exits"].append(found_room_1["id"])
      embed.add_field(name="Mutually Connecting...", value=f"( {found_room_1['displayname']} ) <----> ( {found_room_3['displayname']} )")
    else:
      found_room_1["exits"].append(found_room_3["id"])
      embed.add_field(name="Connecting...", value=f"( {found_room_1['displayname']} ) -----> ( {found_room_3['displayname']} ) ")
  if found_room_4:
    if mutual:
      found_room_1["exits"].append(found_room_4["id"])
      found_room_4["exits"].append(found_room_1["id"])
      embed.add_field(name="Mutually Connecting...", value=f"( {found_room_1['displayname']} ) <----> ( {found_room_4['displayname']}")
    else:
      found_room_1["exits"].append(found_room_4["id"])
      embed.add_field(name="Connecting...", value=f"( {found_room_1['displayname']} ) -----> ( {found_room_4['displayname']} )")
  if found_room_5:
    if mutual:
      found_room_1["exits"].append(found_room_5["id"])
      found_room_5["exits"].append(found_room_1["id"])
      embed.add_field(name="Mutually Connecting...", value=f"( {found_room_1['displayname']} ) <----> ( {found_room_5['displayname']} )")
    else:
      found_room_1["exits"].append(found_room_5["id"])
      embed.add_field(name="Connecting...", value=f"( {found_room_1['displayname']} ) -----> ( {found_room_5['displayname']} )")
  if room1 in (room2, room3, room4, room5):
      embed.add_field(name="WARNING:", value="You are about to connect a room to itself! This will cause a circular loop in that room. Are you sure you want to do this?", inline=False)

  big_dict = {}
  edited_rooms = []
  for room in [found_room_1, found_room_2, found_room_3, found_room_4, found_room_5]:
    if room and room["id"] not in edited_rooms:
      print("adding room to dict:")
      database.pp(room)
      big_dict[room["id"]] = room
      edited_rooms.append(room["id"])
  print("big dict:")
  for subdict in big_dict:
    database.pp(big_dict[subdict])
  #persistent view with ID group
  view = database.PersistentView()
  id_group = database.random_persistent_id(32)
  confirm_button = database.ConfirmButton(random_id=id_group, label="Connect Rooms", confirm=True, action="connect", dict=big_dict)
  cancel_button = database.ConfirmButton(random_id=id_group, label="Cancel", confirm=False, action="cancel", id=found_room_1["id"])
  view.add_item(confirm_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

#provides a list of available rooms
@connectrooms.autocomplete('room1')
async def autocomplete_room1(interaction: discord.Interaction, current: str):
  room_query = database.rooms.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

#provides a list of available rooms
@connectrooms.autocomplete('room2')
async def autocomplete_room2(interaction: discord.Interaction, current: str):
  room_query = database.rooms.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

#provides a list of available rooms
@connectrooms.autocomplete('room3')
async def autocomplete_room3(interaction: discord.Interaction, current: str):
  room_query = database.rooms.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

#provides a list of available rooms
@connectrooms.autocomplete('room4')
async def autocomplete_room4(interaction: discord.Interaction, current: str):
  room_query = database.rooms.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

#provides a list of available rooms
@connectrooms.autocomplete('room5')
async def autocomplete_room5(interaction: discord.Interaction, current: str):
  room_query = database.rooms.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

async def setup(bot):
    bot.add_command(connectrooms)