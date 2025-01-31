import discord
from discord.ext import commands

import database


#Lists the current adventures from the database
@commands.hybrid_command(name= "adventures", description= "A list of all playable adventures")
async def adventures(ctx):
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  guild = ctx.guild
  adventures = database.get_adventures()
  adventure_names = []
  descriptions = []
  authors = []
  word_counts = []
  all_players = []
  all_playcounts = []
  for adventure in adventures:
    word_count = 0
    players = database.get_players_in_adventure(adventure["name"].title())
    if players:
      all_players.append(players)
    else:
      all_players.append("0")
    for roomid in adventure["rooms"]:
      found_room = database.get_room(roomid)
      if found_room:
        word_count += len(found_room["description"].split())
    word_counts.append(word_count)
    adventure_names.append(adventure["name"].title())
    descriptions.append(adventure["description"])
    all_playcounts.append(adventure["total_plays"])
    author_id = adventure["author"]
    author = guild.get_member(author_id)
    if author:
      authors.append(author.display_name)
    else:
      authors.append("Unknown")
  player = database.get_player(ctx.author.id)
  if player and player["guild"] != guild.id:
    old_guild = ctx.client.get_guild(player["guild"])
    if old_guild:
      await ctx.reply(f"You are already a player in a different server:\n{old_guild.name}\n Use /newplayer to delete your old data and start fresh in this server.", ephemeral=True)
      return
    else:
      await ctx.reply("You are not a player in this server. It seems you were a player in a server that was deleted? If this is an error contact @sarnt\nUse /newplayer to start fresh.", ephemeral=True)
      return
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