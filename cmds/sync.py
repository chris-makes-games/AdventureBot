from discord.ext import commands


#syncs the command tree to discord
#this is a global command and will sync to all guilds
#user's discord client will need a restart
@commands.hybrid_command()
async def sync(ctx):
  await ctx.bot.tree.sync()

async def setup(bot):
  bot.add_command(sync)