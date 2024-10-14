from discord.ext import commands

import database
import perms_ctx as permissions


#only used for IDs now but can be edited to fix other things in the future
@commands.hybrid_command(description="Updates all IDs in the database")
async def fixall(ctx, adventure : str):
  #user must be maintainer
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
    return
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return
  found_adventure = database.adventures.find_one({"name": adventure})
  new_rooms = []
  new_start = ""
  if adventure:
    for room_id in found_adventure["rooms"]:
      new_id = database.generate_unique_id()
      database.rooms.update_one({"id": room_id}, {"$set": {"id": new_id}})
      database.ids.update_one({"id": room_id}, {"$set": {"id": new_id}})
      new_rooms.append(new_id)
      if found_adventure["start"] == room_id:
        new_start = new_id
    database.adventures.update_one({"name": adventure}, {"$set": {"rooms": new_rooms, "start": new_start}})
    await ctx.send(f"All IDs updated for adventure {adventure}")


async def setup(bot):
  bot.add_command(fixall)