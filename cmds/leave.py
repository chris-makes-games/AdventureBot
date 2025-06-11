from discord.ext import commands

import database
import perms_ctx as permissions

#Leaves current adventure
@commands.hybrid_command(name= "leave", description= "Leave your current adventure")
async def leave(ctx):
  truename = ctx.author.id
  player = database.get_player(truename)
  guild = ctx.guild
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  #if the guild thread is empty
  if not player["play_thread"]:
    await ctx.reply("You are not in an adventure! Try to /join an adventure first. Use /adventures for a list of available adventures.", ephemeral=True)
    return
  #if the proper thread does not exist
  if not permissions.thread_exists(ctx):
    confirm = await database.confirm_embed(ctx.interaction.id, "It looks like you were in an adventure in a thread that no longer exists. Do you want to leave your adventure and erase your adventure data?", action="leave", channel=None)
    embed = confirm[0]
    view = confirm[1]
    await ctx.defer(ephemeral=True)
    await ctx.reply(embed=embed, view=view, ephemeral=True)
    return
  #if the command isn't sent in the correct thread
  if not permissions.correct_game_thread(ctx):
    guild = ctx.bot.get_guild(player["guild"])
    thread = guild.get_thread(player["play_thread"])
    link = f"https://discord.com/channels/{guild.id}/{thread.id}"
    await ctx.reply(f"You must send this command in your adventure thread. Use /leave in the thread to leave your adventure:\n{link}", ephemeral=True, suppress_embeds=True)
    return
  #the command is successful
  channel = ctx.channel.id
  tuple = await database.confirm_embed(ctx.interaction.id, "Leaving the adventure will erase your adventure progress. Are you sure you want to do this?", "leave" , channel=channel, id=channel)
  embed = tuple[0]
  view = tuple[1]
  await ctx.defer(ephemeral=True)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(leave)