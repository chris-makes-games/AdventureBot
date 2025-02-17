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
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  all_rooms = database.rooms.find()
  for room in all_rooms:
    room_object = Room.from_dict(room)
    room_id = room_object.id
    room_name = room_object.displayname
    print(f"checking room {room_name}")
    print(f"room ID: {room_id}")
    dict = room_object.__dict__
    database.update_room(dict)
    await ctx.send(f"room {room_name} with ID {room_id} updated")

async def setup(bot):
  bot.add_command(updaterooms)