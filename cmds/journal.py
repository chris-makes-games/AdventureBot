from discord import app_commands
from discord.ext import commands

import database


@commands.hybrid_command(name="journal", description="View your journal")
async def journal(ctx):
  player = database.users.find_one({"disc": ctx.author.id})
  if player:
    pass
  else:
    print("ERROR!!!!")
    return

async def setup(bot):
  bot.add_command(journal)