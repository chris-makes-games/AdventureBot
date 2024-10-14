import discord
from discord.ext import commands

import database
import perms_ctx as permissions


@commands.hybrid_command(name="newassistant", description="Add a user as a bot maintenance assistant")
async def newassistant(ctx, user: discord.User):
  id = user.id
  print(f"adding {user} as an assistant")
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You must be a maintainer to add an assistant.")
    return
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return
  if user is None:
    await ctx.send(f"User {user} not found! Must be in this server to add")
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