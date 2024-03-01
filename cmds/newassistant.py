import discord
from discord.ext import commands

import database
import perms_ctx as permissions


@commands.hybrid_command(name="newassistant", description="Add a user as a bot maintenance assistant")
async def newassistant(ctx, user: discord.User):
  id = user.id
  if user is None:
    await ctx.send("User not found! Must be in this guild to add")
    return
  print(f"adding {user} as an assistant")
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You must be a maintainer to add an assistant.")
    return
  if database.botinfo.find_one({"assistants": id}):
    await ctx.reply(f"User {user.mention} is already an assistant")
    return
  document = database.botinfo.find_one({"permissions": "assistants"})
  if not document:
    await ctx.reply("ERROR - no assistant document in database!")
    return
  document["assistants"].append(id)
  database.botinfo.update_one({"permissions": "assistants"}, {"$set": document})
  await ctx.reply(f"Added {user.mention} as an assistant")

async def setup(bot):
  bot.add_command(newassistant)