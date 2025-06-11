from discord.ext import commands

import database


#command to suggest featured stories
@commands.hybrid_command(name= "feature", description= "Submit a story to potentially be featured")
async def feature(ctx):
  truename = ctx.author.id
  tuple = await database.feature_embed(ctx.interaction.id, truename)
  embed = tuple[0]
  view = tuple[1]
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(feature)