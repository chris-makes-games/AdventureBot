from discord.ext import commands

import database


#deactivated valentines command, saving for later use just in case
@commands.hybrid_command(name= "cupid", description= "Use this to submit your valentine for the event")
async def cupid(ctx):
  truename = ctx.author.id
  tuple = await database.valentine_embed(truename)
  embed = tuple[0]
  view = tuple[1]
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(cupid)