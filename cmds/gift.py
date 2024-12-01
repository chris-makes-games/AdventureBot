from discord.ext import commands

import database

#secret santa command
@commands.hybrid_command(name= "gift", description= "Use to sign up for the winter gift exchange")
async def gift(ctx):
  truename = ctx.author.id
  tuple = await database.gifts_embed(truename)
  embed = tuple[0]
  view = tuple[1]
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(gift)