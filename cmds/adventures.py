import discord
from discord.ext import commands

import database


#Lists the current adventures from the database
@commands.hybrid_command(name= "adventures", description= "A list of all playable adventures")
async def adventures(ctx):
  guild = ctx.guild
  adventures = database.get_adventures()
  adventure_names = []
  descriptions = []
  authors = []
  word_counts = []
  all_players = []
  all_playcounts = []
  if guild is None:
    return
  for adventure in adventures:
    word_count = 0
    players = database.get_players_in_adventure(adventure["name"])
    if players:
      all_players.append(players)
    else:
      all_players.append("0")
    for roomid in adventure["rooms"]:
      found_room = database.get_room(roomid)
      if found_room:
        word_count += len(found_room["description"].split())
    word_counts.append(word_count)
    adventure_names.append(adventure["name"])
    descriptions.append(adventure["description"])
    all_playcounts.append(adventure["total_plays"])
    author_id = adventure["author"]
    author = guild.get_member(author_id)
    if author:
      authors.append(author.display_name)
    else:
      authors.append("Unknown")
  player = database.get_player(ctx.author.id)
  if player:
    embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use /join to start an adventure. More adventures will be available later!", color=0x00ff00)
  else:
    embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Before you can try an adventure, you must first use /newplayer to get started. More adventures will be available later!", color=0x00ff00)
  for i in range(len(adventure_names)):
    name = adventure_names[i]
    description = descriptions[i]
    author = authors[i]
    word_count = word_counts[i]
    players = all_players[i]
    total_plays = all_playcounts[i]
    embed.add_field(name=name.title(), value=f"{description}\nCreated by: ***{author}***\nWord count: {word_count}\nCurrent Players: {players}\nTotal Plays: {total_plays}", inline=False)
  await ctx.reply(embed=embed, ephemeral=True)
  return

async def setup(bot):
  bot.add_command(adventures)