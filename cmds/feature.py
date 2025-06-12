from discord.ext import commands

from discord import app_commands

import database

#command to send emdbed for featured story suggestion button

@commands.hybrid_command(name= "feature", description= "Submit a story to potentially be featured")
async def feature(ctx):
  truename = ctx.author.id
  tuple = await database.feature_embed(ctx.interaction.id, truename)
  embed = tuple[0]
  view = tuple[1]

  await ctx.send(embed=embed, view=view, ephemeral=False)


async def setup(bot):
  bot.add_command(feature)