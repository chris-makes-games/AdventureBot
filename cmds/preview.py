from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


# Shows what a room/item will look like
# Can also preview player info, but only as a maintainer
@commands.hybrid_command(name="preview", description="Shows a preview of a key or room as it appears in the game")
@app_commands.choices(choices=[
  app_commands.Choice(name="Key", value="Key"),
  app_commands.Choice(name="Room", value="Room"),
  app_commands.Choice(name="Player", value="Player")
])
async def preview(ctx, type: str, id: str):
  #allows to look at a player if admin
  if type == "Player":
    if not permissions.check_any_admin(ctx):
      await ctx.reply("You do not have permission to use this command to look at player data!", ephemeral=True)
      return
    else:
      player = database.users.find_one({"disc": ctx.author.id})
      if not player:
        await ctx.reply(f"Player {id} not found!", ephemeral=True)
        return
      player_info = []
      for data in player:
        player_info.append(f"{data}: {player[data]}\n")
      await ctx.reply(f"Player {id}:\n" + "".join(player_info), ephemeral=True)
  #allows to look at room if its their own room or admin
  elif type == "Room":
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
        room_info.append(f"{data}: {room[data]}\n")
      await ctx.reply(f"Room {id}:\n" + "".join(room_info), ephemeral=True)
      return
  #allows to look at key if its their own key or admin
  elif type == "Key":
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
        key_info.append(f"{data}: {key[data]}\n")
      await ctx.reply(f"Key {id}:\n" + "".join(key_info), ephemeral=True)

async def setup(bot):
  bot.add_command(preview)