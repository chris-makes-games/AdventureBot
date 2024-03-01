from discord.ext import commands

import database
import perms_ctx as permissions


@commands.hybrid_command(name="newmaintainer", description="Adds a new maintainer to the database")
async def newmaintainer(ctx, user: str):
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.")
    return
  if database.botinfo.find_one({"maintainers": user}):
    await ctx.reply(f"User {user} is already a maintainer")
    return
  await database.botinfo.update_one({"maintainers": user}, {"$set": user})

# @newmaintainer.autocomplete("user")
# async def newmaintainer_autocomplete(ctx, user: str):
#   return [user for user in ctx.guild.members if user.name.startswith(user)]

async def setup(bot):
  bot.add_command(newmaintainer)