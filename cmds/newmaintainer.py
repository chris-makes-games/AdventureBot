import discord
from discord.ext import commands

import database
import perms_ctx as permissions


@commands.hybrid_command(name="newmaintainer", description="Add a user as a bot maintainer")
async def newmaintainer(ctx, user: discord.User):
  id = user.id
  if user is None:
    await ctx.send("User not found! Must be in this guild to add")
    return
  print(user)
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You must be a maintainer to add a maintainer.")
    return
  if database.botinfo.find_one({"maintainers": id}):
    await ctx.reply(f"User {user.mention} is already a maintainer")
    return
  document = database.botinfo.find_one({"permissions": "maintainers"})
  if not document:
    await ctx.reply("ERROR - no maintainer document in database!")
    return
  document["maintainers"].append(id)
  database.botinfo.update_one({"permissions": "maintainers"}, {"$set": document})
  await ctx.reply(f"Added {user.mention} as a maintainer")

async def setup(bot):
  bot.add_command(newmaintainer)