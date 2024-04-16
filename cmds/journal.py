from discord import app_commands
from discord.ext import commands

import database


@commands.hybrid_command(name="journal", description="View your journal")
async def journal(ctx):
  player = database.users.find_one({"disc": ctx.author.id})
  if player:
    embed, view = await database.embed_journal(player)
  else:
    print("ERROR!!!!")
    return
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(journal)