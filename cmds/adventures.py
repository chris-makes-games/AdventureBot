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
  word_counts = []
  if guild is None:
    return
  for adventure in adventures:
    word_count = 0
    for roomid in adventure["rooms"]:
      found_room = database.get_room(roomid)
      if found_room:
        word_count += len(found_room["description"].split())
    word_counts.append(word_count)
    adventure_names.append(adventure["name"])
    descriptions.append(adventure["description"])
    author_id = adventure["author"]
    author = guild.get_member(author_id)
    if author:
      authors.append(author.display_name)
    else:
      authors.append("Unknown")
  embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use /join to start an adventure. More adventures will be available later!", color=0x00ff00)
  for i in range(len(adventure_names)):
    embed.add_field(name=adventure_names[i].title(), value=f"{descriptions[i]}\nCreated by: ***{authors[i]}***\nWord count: {word_counts[i]}", inline=False)
  await ctx.reply(embed=embed)
  return

async def setup(bot):
  bot.add_command(adventures)