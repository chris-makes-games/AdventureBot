import discord
from discord import app_commands
from discord.ext import commands

import database
import formatter
from player import Player


#player join an adventure
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
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #cancel if player is in an adventure in this guild
  #need to check every guild/id pair
  guild = ctx.guild
  all_threads = player["guilds_threads"]
  for guild_thread_list in all_threads:
    if any(guild.id == guild_thread for guild_thread in guild_thread_list):
      thread_found = guild.get_thread(guild_thread_list[1])
      #if the thread doesn't exist in guild
      if not thread_found:
        await ctx.reply("It looks like you were in an adventure in a thread that no longer exists. Your old adventure thread is being closed...", ephemeral=True)
        all_threads.remove(guild_thread_list)
        update_player = Player(discord=truename, room=None, displayname=displayname, guilds_threads=all_threads)
        #delete thread, update player in database
        #continues to joining the adventure
        database.update_player(update_player.__dict__)
      #give player their adventure thread
      else:
        adventure_link = f"https://discord.com/channels/{guild.id}/{thread_found.id}"
        await ctx.reply(f"{ctx.author.mention}, You are already in an adventure in this server! Click this link to go there:\n{adventure_link}", ephemeral=True, suppress_embeds=True)
        return
  adventure = database.get_adventure(adventure_name)
  #cancel if the adventure they entered is not found
  if not adventure:
    all_adventures = database.get_adventures()
    embed = discord.Embed(title=f"Error - No Adventure named '{adventure_name}'", description="Adventure '" + adventure_name + "' was not found. Please !join one of these adventures to begin:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
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
    #adds the guild, thread pair to the guilds_threads list
    threads = player["guilds_threads"]
    threads.append([guild.id, thread.id])
    #player object generated from player class
    player = Player(discord=truename, displayname=displayname, room=adventure["start"], guilds_threads=threads)
    database.update_player(player.__dict__)
    room = database.get_player_room(truename)
    #error if the start room is not found
    if room is None:
      print("Error! Room is None!")
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
      author = "Unknown"
    all_items = []
    new_items = []
    #embed message for all rooms
    tuple = database.embed_room(all_items, new_items, room["displayname"], room, author)
    embed = tuple[0]
    view = tuple[1]
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
    possible_adventures = [adv["nameid"] for adv in adventures_query if current.lower() in adv["nameid"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_adventures[:10]]

async def setup(bot):
  bot.add_command(join)