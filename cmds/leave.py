import discord
from discord.ext import commands

import database
import formatter
import perms_ctx as permissions


#Leaves current adventure
@commands.hybrid_command(name= "leave", description= "Leave an adventure")
async def leave(ctx):
    truename = ctx.author.id
    name = ctx.author.display_name 
    player = database.get_player(truename)
    if player:
      if not player["game_threads"]:
        await ctx.reply("You are not in an adventure!")
        return
      if not permissions.thread_check(ctx):
        embed = discord.Embed(title="Error", description="You must use this command in a game thread! Try going to one of your threads:", color=0xff0000)
        for thread in player["game_threads"]:
          thread_obj = ctx.guild.get_thread(thread)
          thread_link = f"https://discord.com/channels/{ctx.guild.id}/{thread}"
          embed.add_field(name=thread_obj.name, value=thread_link, inline=False)
        await ctx.reply(embed=embed)
        return
        
      channel = ctx.channel.id
      tuple = await database.confirm_embed("Leaving the adventure will erase your adventure progress. Are you sure you want to do this?", "leave" , channel=channel, id=channel)
      embed = tuple[0]
      view = tuple[1]
      await ctx.reply(embed=embed, view=view, ephemeral=True)
    else:
      embed = formatter.embed_message(name, "Error", "notplayer" , "red")
      await ctx.reply(embed=embed, ephemeral=True)

async def setup(bot):
  bot.add_command(leave)