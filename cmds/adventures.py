from discord.ext import commands
from discord import app_commands
import database
import discord

#Lists the current adventures from the database
@commands.hybrid_command(name= "adventures", description= "A list of all playable adventures")
async def adventures(ctx):
  guild = ctx.guild
  adventures = database.get_adventures()
  adventure_names = []
  descriptions = []
  authors = []
  if guild is None:
    return
  for adventure in adventures:
    adventure_names.append(adventure["nameid"])
    descriptions.append(adventure["description"])
    author_id = adventure["author"]
    author = guild.get_member(author_id)
    if author:
      authors.append(author.display_name)
    else:
      authors.append("Unknown")
  embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use /join to start an adventure. More adventures will be available later!", color=0x00ff00)
  for i in range(len(adventure_names)):
    embed.add_field(name=adventure_names[i].title(), value=descriptions[i] + "\n*Created by: " + authors[i] + "*", inline=False)
  await ctx.reply(embed=embed)
  return

async def setup(bot):
  bot.add_command(adventures)