import discord
from discord import app_commands
from discord.ext import commands

import database
import formatter
from player import Player


#players join an adventure
#players may only be in one adventure at a time, per server
@commands.hybrid_command(name="join", description="Join an adventure")
async def join(ctx, adventure_name : str):
  truename = ctx.author.id
  displayname = ctx.author.display_name
  channel = ctx.channel
  player = database.get_player(truename)
  #cancel if no player is found in the database
  if not player:
    embed = formatter.embed_message(displayname, "Error", "notplayer" , "red")
    await ctx.reply.send_message(embed=embed, ephemeral=True)
    return
  #check if player is in an adventure in this guild
  if player and ctx.guild.id in player["guilds"]:
    await ctx.reply(f"Player {player['displayname']} is already in an adventure on this server!", ephemeral=True)
    return
  if adventure_name == "":
    all_adventures = database.get_adventures()
    embed = discord.Embed(title="Error - Need adventure", description="You need to specify an adventure to join. Use !join <adventure name here>\nRefer to this list of available adventures:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  adventure = database.get_adventure(adventure_name)
  if not adventure:
    all_adventures = database.get_adventures()
    embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please !join one of these adventures to begin:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  else:
    guild = ctx.guild
    channel = ctx.channel
    if not channel:
      await ctx.reply("Error - Channel not found", ephemeral=True)
      return
    if channel.type == discord.ChannelType.text:
      thread = await channel.create_thread(name=adventure_name + "'s " + adventure_name)
    else:
      await ctx.reply("Error - Channel is not a text channel", ephemeral=True)
      return
    channel_id = thread.id
    #if the player is in the database, update the player's game thread ids and guilds list
    if player:
      new_guilds = player["guilds"].append(guild.id)
      new_threads = player["game_threads"].append(channel_id)
      player = Player(discord=truename, displayname=displayname, room=adventure["start"], guilds=new_guilds, game_threads=new_threads)
      database.update_player(player.__dict__)
    else:
    #if the player is not in the database, create a new player object and add to database
      player = Player(discord=truename, displayname=displayname, room=adventure["start"], guilds=[guild.id], game_threads=[channel_id])
      database.new_player(player.__dict__)
    room = database.get_player_room(truename)
    if room is None:
      print("Error! Room is None!")
      embed = formatter.embed_message(displayname, "Error", "noroom", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      return
    if guild is None:
      print("Error! Guild is None!")
      embed = formatter.embed_message(displayname, "Error", "noguild", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      return
    room_author = room["author"]
    author = guild.get_member(room_author).display_name
    if not author:
      author = "Unknown"
    all_items = []
    new_items = []
    tuple = database.embed_room(all_items, new_items, room["displayname"], room, author)
    embed = tuple[0]
    view = tuple[1]
    #comment to delete command after success:
    await thread.send(ctx.author.mention + "You have sucessfully begun an adventure. Use the buttons below to play. If you have questions, ask a moderator",embed=embed, view=view)

# Autocompletion function for adventure_name in join command
@join.autocomplete('adventure_name')
async def autocomplete_join(ctx, current: str):
    adventures_query = database.get_adventures()
    possible_adventures = [adv["nameid"] for adv in adventures_query if current.lower() in adv["nameid"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_adventures[:10]]

async def setup(bot):
  bot.add_command(join)