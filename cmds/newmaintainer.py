import discord
from discord.ext import commands

import database
import perms_ctx as permissions


@commands.hybrid_command(name="newmaintainer", description="Add a user as a bot maintainer")
async def newmaintainer(ctx, user: discord.User):
  id = user.id
  print(user)
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You must be a maintainer to add a maintainer.")
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
  if database.botinfo.find_one({"maintainers": id}):
    await ctx.reply(f"User {user} is already a maintainer")
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