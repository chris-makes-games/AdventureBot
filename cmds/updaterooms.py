from discord.ext import commands

import database
import perms_ctx as permissions
from room import Room


#pulls all rooms and updates them according to class attributes
#can really mess things up!
@commands.hybrid_command(description="Updates all rooms in the database according to the room class")
async def updaterooms(ctx):
  #user must be maintainer
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
    return
  all_rooms = database.rooms.find()
  for room in all_rooms:
    room_object = Room(dict=room)
    room_id = room_object.id
    room_name = room_object.displayname
    print(f"checking room {room_name}")
    print(f"room ID: {room_id}")
    dict = room_object.__dict__
    database.update_room(dict)
    await ctx.send(f"room {room_name} with ID {room_id} updated")

async def setup(bot):
  bot.add_command(updaterooms)