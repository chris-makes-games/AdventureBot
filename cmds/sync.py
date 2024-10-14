from discord.ext import commands

import perms_ctx as permissions


#syncs the command tree to discord
#this is a global command and will sync to all guilds
#user's discord client will need a restart
@commands.hybrid_command()
async def sync(ctx):
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
    return
  await ctx.bot.tree.sync()
  await ctx.reply("Commands Syncd", ephemeral=True)
  

async def setup(bot):
  bot.add_command(sync)