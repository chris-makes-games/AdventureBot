import discord
from discord.ext import commands

import database
import formatter
import perms_ctx as permissions
from player import Player


#Leaves current adventure
@commands.hybrid_command(name= "leave", description= "Leave your current adventure")
async def leave(ctx):
    truename = ctx.author.id
    displayname = ctx.author.display_name
    player = database.get_player(truename)
    guild = ctx.guild
    #if the player is not in the database
    if not player:
        await ctx.reply("You are not registered as a player! You must use /newplayer to begin", ephemeral=True)
        return
    #if the list of guilds/threads is empty
    if not player["guilds_threads"]:
      await ctx.reply("You are not in an adventure! Try to /join an adventure first. Use /adventures for a list of available adventures.", ephemeral=True)
      return
    all_threads = player["guilds_threads"]
    for guild_thread_pair in all_threads:
      if any(guild.id == guild_thread for guild_thread in guild_thread_pair):
        thread_found = guild.get_thread(guild_thread_pair[1])
        if not thread_found:
          embed = discord.Embed(title="Wrong Server", description=f"It looks like you are in an adventure in another server. If you want to leave that adventure, type /leave in that advenutre's thread. Your active threads:", color=discord.Color.red())
          for guild_thread_pair in all_threads:
            guild = ctx.bot.get_guild(guild_thread_pair[0])
            if guild.get_thread(guild_thread_pair[1]):
              link = f"https://discord.com/channels/{guild.id}/{guild_thread_pair[1]}"
              embed.add_field(name=guild.name, value=link)
          view = discord.ui.View()
          await ctx.reply(embed=embed, view=view, ephemeral=True)
    if not permissions.thread_check(ctx):
      embed = discord.Embed(title="Error", description="You must use this command in a game thread! Try going to one of your threads:", color=0xff0000)
      for thread in player["guilds_threads"]:
        thread_obj = guild.get_thread(thread[1])
        #if the thread was deleted
        #deletes guild/thread, updates the database
        if not thread_obj:
          await ctx.reply(f"It looks like you were in an adventure in a thread that no longer exists. Your old adventure thread in the {guild.name} server will be closed.", ephemeral=True)
          all_threads.remove(thread)
          update_player = Player(discord=truename, room=None, displayname=displayname, guilds_threads=all_threads)
          database.update_player(update_player.__dict__)
          return
        thread_link = f"https://discord.com/channels/{ctx.guild.id}/{thread_obj.id}"
        embed.add_field(name=f"Adventure in {guild.name}:", value=thread_link, inline=False)
      view = discord.ui.View()
      await ctx.reply(embed=embed, view=view, ephemeral=True)
      return
    channel = ctx.channel.id
    tuple = await database.confirm_embed("Leaving the adventure will erase your adventure progress. Are you sure you want to do this?", "leave" , channel=channel, id=channel)
    embed = tuple[0]
    view = tuple[1]
    await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(leave)