import formatter

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions
from adventure import Adventure


#makes a new adventure in the database
@commands.hybrid_command(name="newadventure", description="Create a new adventure")
@app_commands.describe(name="The name of the adventure", description="A brief description of the adventure for new players", 
epilogue="Whether the adventure allows players to freely explore the adventure after reaching an ending. Defaults to False.")
async def newadventure(ctx, name: str, description: str, epilogue: bool=False):
  truename = ctx.author.id
  displayname = ctx.author.display_name
  channel = ctx.channel
  #if the player is not in the database
  player = database.get_player(truename)
  if not player:
    embed = formatter.blank_embed(displayname, "Error", "You are not a player. Please use /newplayer to begin. You can create an adventure once you've been added to the database", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if the player already made an adventure
  if player["owned_adventures"]:
    embed = formatter.blank_embed(displayname, "Error", "You already have an adventure! You can only have one. Please use /editadventure to edit your adventure.", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if they are in giantessworld, make sure they are an architect
  if ctx.guild.id == 730468423586414624 and not permissions.has_role(ctx, "architect"):
    embed = formatter.blank_embed(displayname, "Error", "You do not have permission to create an adventure. You need the architect role, please go to #role-select to get the role or contact Ironially-Tall", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  # Check if the author already has an adventure to edit
  if player["edit_thread"]:
    adventure = database.adventures.find_one({"author": truename})
    thread = ctx.guild.get_thread(player["edit_thread"][0])
    #if the thread is broken/deleted, make a new one
    if not thread:
      embed = formatter.blank_embed(displayname, "Error", "It seems like the thread you were using to edit your previous adventure has been deleted. A new thread is being generated...", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      thread = await channel.create_thread(name=f"{displayname} editing {player['edit_thread'][1]}")
      await thread.send(ctx.author.mention + ", your new thread is ready. Use the commands to add/edit keys and rooms here.")
      database.update_player({'disc': truename, 'edit_thread': [thread.id, adventure.name]})
      link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
      await ctx.reply(f"A new thread was created to edit your adventure:\n{link}", ephemeral=True, suppress_embeds=True)
      return
    #if the thread is still active, reply with link
    else:
      link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
      embed = formatter.blank_embed(displayname, "Error", f"You already have an existing adventure. You cannot create more than one. Go to your editing thread to modify your adventure:\n{link}", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      return
  #if no adventure found, create a new one
  else:
    start_room = database.create_blank_room(truename)
    start = start_room.id
    adventure = Adventure(name=name, start=start, rooms=[start], description=description, epilogue=epilogue, author=truename)
    database.adventures.insert_one(adventure.__dict__)
    # Then, create a new thread for editing this adventure
    database.pp("creating adventure edit channel as thread in channel: " + str(channel))
    if channel and channel.type == discord.ChannelType.text:
      thread = await channel.create_thread(name=f"{displayname} editing {name}")
      await thread.send(ctx.author.mention + ", your adventure is ready. Use the commands to add/edit keys and rooms in this thread. A start room was automatically created for you. Use /editroom to edit it.")
        # Update the player's editthread field with the new thread ID
      database.update_player({'disc': truename, 'edit_thread': [thread.id, adventure.name], 'owned_adventures': [name]})
      link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
      embed = formatter.blank_embed(displayname, "Success", f"{name} was created and your edit thread is ready:\n{link}", "green")
      await ctx.reply(embed=embed, ephemeral=True)

async def setup(bot):
  bot.add_command(newadventure)