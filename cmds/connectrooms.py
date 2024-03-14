import discord
from discord import app_commands
from discord.ext import commands

import database


@commands.hybrid_command(name="connectrooms", description="Connect one room to others. Mutual for two-way connects")
async def connectrooms(ctx, room1: str, room2: str, 
            room3: str | None = None, 
            room4: str | None = None, 
            room5: str | None = None,
            mutual: bool = False):
  room_1 = database.get_room(room1)
  room_2 = database.get_room(room2)
  room_3 = database.get_room(room3) if room3 else None
  room_4 = database.get_room(room4) if room4 else None
  room_5 = database.get_room(room5) if room5 else None

  if not room_1:
    await ctx.reply(f"ERROR: Room '{room1}' not found.", ephemeral=True)
    return
  if not room_2:
    await ctx.reply(f"ERROR: Room '{room2}' not found.", ephemeral=True)
    return

  embed = discord.Embed(title="Update Connecttions", description="Review the changes below and confirm the new connections:")
  if mutual:
    room_1["exits"].append(room_2["id"])
    room_2["exits"].append(room_1["id"])
    embed.add_field(name="Mutually Connected:", value=f"( {room_1['displayname']} ) <----> ( {room_2['displayname']} )")
  else:
    room_1["exits"].append(room_2["id"])
    embed.add_field(name="Connected:", value=f"( {room_1['displayname']} ) -----> ( {room_2['displayname']} )")
  if room_3:
    if mutual:
      room_1["exits"].append(room_3["id"])
      room_3["exits"].append(room_1["id"])
      embed.add_field(name="Mutually Connected:", value=f"( {room_1['displayname']} ) <----> ( {room_3['displayname']} )")
    else:
      room_1["exits"].append(room_3["id"])
      embed.add_field(name="Connected:", value=f"( {room_1['displayname']} ) -----> ( {room_3['displayname']} ) ")
  if room_4:
    if mutual:
      room_1["exits"].append(room_4["id"])
      room_4["exits"].append(room_1["id"])
      embed.add_field(name="Mutually Connected:", value=f"( {room_1['displayname']} ) <----> ( {room_4['displayname']}")
    else:
      room_1["exits"].append(room_4["id"])
      embed.add_field(name="Connected:", value=f"( {room_1['displayname']} ) -----> ( {room_4['displayname']} )")
  if room_5:
    if mutual:
      room_1["exits"].append(room_5["id"])
      room_5["exits"].append(room_1["id"])
      embed.add_field(name="Mutually Connected:", value=f"( {room_1['displayname']} ) <----> ( {room_5['displayname']} )")
    else:
      room_1["exits"].append(room_5["id"])
      embed.add_field(name="Connected:", value=f"( {room_1['displayname']} ) -----> ( {room_5['displayname']} )")

  dict = {}
  for room in [room_1, room_2, room_3, room_4, room_5]:
    if room:
      dict[room["id"]] = room
  confirm_button = database.ConfirmButton(label="Connect Rooms", confirm=True, action="connect", id=room_1["id"], dict=dict)
  view = discord.ui.View()
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=room_1["id"])
  view.add_item(confirm_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    bot.add_command(connectrooms)