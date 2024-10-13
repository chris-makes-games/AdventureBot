import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


# Shows what a room/item will look like
# Can also preview player info, but only as a maintainer
@commands.hybrid_command(name="preview", description="Shows a preview of a key or room as it appears in the game")
@app_commands.choices(type=[
    app_commands.Choice(name="Key", value="Key"),
    app_commands.Choice(name="Room", value="Room"),
    app_commands.Choice(name="Player", value="Player"),
    ])
async def preview(ctx, type: app_commands.Choice[str], id : str):
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  #allows to look at a player if admin
  if type.name == "Player":
    print(f"finding player: {id}")
    if not permissions.check_any_admin(ctx):
      await ctx.reply("You do not have permission to use this command to look at player data!", ephemeral=True)
      return
    else:
      try:
        player = database.users.find_one({"disc": int(id)})
        if not player:
          await ctx.reply(f"Player {id} not found!", ephemeral=True)
          return
      except Exception as e:
        print(f"ERROR! {e}")
        await ctx.reply(f"ERROR - {e}", ephemeral=True)
        return
      player_info = []
      for data in player:
        if data == "_id":
          continue
        value = str(player[data])
        if value:
          value = value.replace("\\n","\n")
          data = "**" + data + "**"
        player_info.append(f"{data}: {value}\n")
      await ctx.reply("**Player Preview**:\n" + "".join(player_info), ephemeral=True)
  #allows to look at room if its their own room or admin
  elif type.name == "Room":
    room = database.rooms.find_one({"id": id})
    if not room:
      await ctx.reply(f"Room {id} not found!", ephemeral=True)
      return
    if ctx.author.id != room["author"] and not permissions.check_any_admin(ctx):
      await ctx.reply("You do not have permission to view that room!", ephemeral=True)
      return
    else:
      room_info = []
      for data in room:
        if data == "_id":
          continue
        value = str(room[data])
        if value:
          value = value.replace("\\n","\n")
          data = "**" + data + "**"
        room_info.append(f"{data}: {value}\n")
      await ctx.reply("**Room Preview**:\n" + "".join(room_info), ephemeral=True)
      return
  #allows to look at key if its their own key or admin
  elif type.name == "Key":
    key = database.keys.find_one({"id": id})
    if not key:
      await ctx.reply(f"Key {id} not found!", ephemeral=True)
      return
    if ctx.author.id != key["author"] and not permissions.check_any_admin(ctx):
      await ctx.reply("You do not have permission to view that key!", ephemeral=True)
      return
    else:
      key_info = []
      for data in key:
        if data == "_id":
          continue
        value = str(key[data])
        if value:
          value = value.replace("\\n","\n")
        key_info.append(f"**{data}:** {key[data]}\n")
      await ctx.reply("**Key Preview**:\n" + "".join(key_info), ephemeral=True)

#autocompletes the IDs of available items by author
@preview.autocomplete('id')
async def autocomplete_id(interaction: discord.Interaction, current: str):
  type = interaction.namespace["type"].lower()
  room_query = database.ids.find(
    {"author": interaction.user.id,
     "type": type,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}},
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

async def setup(bot):
  bot.add_command(preview)