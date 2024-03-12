from discord.ext import commands
from discord import app_commands
import database
import discord


@commands.hybrid_command(name="connectrooms", description="Connect two or more rooms together. Set mutual to true to make the rooms mutually connect together, instead of a one-way connection.")
async def connectrooms(ctx, room1: str, room2: str, 
            room3: str | None = None, 
            room4: str | None = None, 
            room5: str | None = None,
            mutual: bool = False):
  room_1 = database.get_room(room1)
  room_2 = database.get_room(room2)
  if room3:
    room_3 = database.get_room(room3)
  else:
    room_3 = None
  if room4:
    room_4 = database.get_room(room4)
  else:
    room_4 = None
  if room5:
    room_5 = database.get_room(room5)
  else:
    room_5 = None

  if not room_1:
    await ctx.reply(f"ERROR: Room '{room1}' not found.", ephemeral=True)
    return
  if not room_2:
    await ctx.reply(f"ERROR: Room '{room2}' not found.", ephemeral=True)
    return

  embed = discord.Embed(title=f"Update Connecttions", description="Review the changes below and confirm the new connections:")
  if mutual:
    room_1["exits"].append(room_2["id"])
    room_2["exits"].append(room_1["id"])
    embed.add_field(name=f"Mutually Connected:", value=f"room {room_1['displayname']} <----> room {room_2['displayname']}")
  else:
    room_1["exits"].append(room_2["id"])
    embed.add_field(name=f"Connected:", value=f"room {room_1['displayname']} -----> room {room_2['displayname']}")
  if room_3:
    if mutual:
      room_1["exits"].append(room_3["id"])
      room_3["exits"].append(room_1["id"])
      embed.add_field(name=f"Mutually Connected:", value=f"room {room_1['displayname']} <----> room {room_3['displayname']}")
    else:
      room_1["exits"].append(room_3["id"])
      embed.add_field(name=f"Connected:", value=f"room {room_1['displayname']} -----> room {room_3['displayname']}")
  if room_4:
    if mutual:
      room_1["exits"].append(room_4["id"])
      room_4["exits"].append(room_1["id"])
      embed.add_field(name=f"Mutually Connected:", value=f"room {room_1['displayname']} <----> room {room_4['displayname']}")
    else:
      room_1["exits"].append(room_4["id"])
      embed.add_field(name=f"Connected:", value=f"room {room_1['displayname']} -----> room {room_4['displayname']}")
  if room_5:
    if mutual:
      room_1["exits"].append(room_5["id"])
      room_5["exits"].append(room_1["id"])
      embed.add_field(name=f"Mutually Connected:", value=f"room {room_1['displayname']} <----> room {room_5['displayname']}")
    else:
      room_1["exits"].append(room_5["id"])
      embed.add_field(name=f"Connected:", value=f"room {room_1['displayname']} -----> room {room_5['displayname']}")

  dict = {}
  for room in [room_1, room_2, room_3, room_4, room_5]:
    dict[room["id"]] = room
  confirm_button = database.ConfirmButton(label="Connect Rooms", confirm=True, action="connect", id=room_1["id"], dict=dict)
  view = discord.ui.View()
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=room_1["id"])
  view.add_item(confirm_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    bot.add_command(connectrooms)