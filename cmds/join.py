import formatter

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions
from player import Player


#player join an adventure
#players may only be in one adventure at a time
@commands.hybrid_command(name="join", description="Join an adventure")
async def join(ctx, adventure_name : str):
  truename = ctx.author.id
  displayname = ctx.author.display_name
  channel = ctx.channel
  adventure = database.get_adventure(adventure_name)
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  #if the correct thread does not exist anymore
  if player["play_thread"] and not permissions.thread_exists(ctx):
    await ctx.reply("It looks like you were in an adventure in a thread that no longer exists. Your old adventure is being deleted and a new one is being created...", ephemeral=True)
  #if the player is already in an adventure
  elif player["play_thread"]:
    play_thread = player["play_thread"]
    guild = ctx.bot.get_guild(player["guild"])
    thread = guild.get_thread(play_thread)
    link = f"https://discord.com/channels/{guild.id}/{thread.id}"
    await ctx.reply(f"You are already in an adventure! If you want to start a new adventure, you must use /leave in this one first:\n{link}", ephemeral=True, suppress_embeds=True)
    return
  #if the adventure they entered is not found
  if not adventure:
    all_adventures = database.get_adventures()
    embed = discord.Embed(title=f"Error - No Adventure named '{adventure_name}'", description="Adventure '" + adventure_name + "' was not found. Please !join one of these adventures to begin:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["name"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if adventure was found, command succeeds
  else:
    guild = ctx.guild
    channel = ctx.channel
    #creates thread if channel is a text channel
    if channel.type == discord.ChannelType.text:
      thread = await channel.create_thread(name=displayname + "'s " + adventure_name.title())
    else:
      await ctx.reply("Error - Channel is not a text channel.", ephemeral=True)
      return
    #player object generated from player class
    player = Player(discord=truename, displayname=displayname, room=adventure["start"], guild=guild.id, play_thread=thread.id)
    database.update_player(player.__dict__)
    room = database.get_player_room(truename)
    #error if the start room is not found
    if room is None:
      print("Error! Start room not found!")
      embed = formatter.embed_message(displayname, "Error", "noroom", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      return
    #error if there is no guild
    if guild is None:
      print("Error! Guild is None!")
      embed = formatter.embed_message(displayname, "Error", "noguild", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      return
    room_author = room["author"]
    author = guild.get_member(room_author).display_name
    #if the author is not found, set to Unknown
    if not author:
      author = "Error - Unknown"
    new_keys = room["keys"]
    #embed message for all rooms
    embed, view, leftover_list = await database.embed_room(ctx.interaction.id, player_dict=player.__dict__, new_keys=new_keys, author=author, room_dict=room, title=room["displayname"], guild=ctx.guild)

    #sends a message in the thread to begin
    #mentions the user to add them to the thread
    await thread.send(ctx.author.mention + "You have sucessfully begun an adventure. Use the buttons below to play. If you have questions, ask a moderator",embed=embed, view=view)
    #sends a message in the original channel with thread link
    message_link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
    await ctx.reply(f"You have sucessfully begun an adventure. Go to the thread to play!\n{message_link}", ephemeral=True, suppress_embeds=True)

# Autocompletion function for adventure_name in join command
@join.autocomplete('adventure_name')
async def autocomplete_join(interaction : discord.Interaction, current: str):
    adventures_query = database.get_adventures()
    possible_adventures = [adv["name"].title() for adv in adventures_query if current.lower() in adv["name"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_adventures[:10]]

async def setup(bot):
  bot.add_command(join)