from discord.ext import commands
from discord import app_commands
import discord
import database
import formatter
import perms_ctx as permissions

#makes a new adventure in the database
@commands.hybrid_command(name="newadventure", description="Create a new adventure")
async def newadventure(ctx):
  truename = ctx.author.id
  name = ctx.author.display_name
  channel = ctx.channel
  #if the player is not in the database
  player = database.get_player(truename)
  if not player:
    embed = formatter.blank_embed(name, "Error", "You are not a player. Please use /newplayer to begin. You can create an adventure once you've been added to the database", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if they are in giantessworld, make sure they are an architect
  if ctx.guild.id == 730468423586414624:
    if not permissions.has_role(ctx, "architect"):
      embed = formatter.blank_embed(name, "Error", "You do not have permission to create an adventure. You need the architect role, please go to #role-select to get the role or contact Ironially-Tall", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      return
  # Check if the author already has an adventure to edit
  if database.testadventures.find_one({"author": truename}):
    thread = ctx.guild.get_thread(player["edit_thread"])
    #if the thread is broken/deleted, make a new one
    if not thread:
      embed = formatter.blank_embed(name, "Error", "It seems like the thread you were using to edit your previous adventure has been deleted. A new thread is being generated...", "red")
      await ctx.reply(embed=embed, ephemeral=True)
      thread = await channel.create_thread(name=f"{name} editing an adventure")
      await thread.send(ctx.author.mention + " is editing an adventure.")
      database.update_player({'disc': truename, 'edit_thread_id': thread.id})
      link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
      await ctx.reply(f"A new thread was created to edit your adventure:\n{link}", ephemeral=True, suppress_embeds=True)
      return
    #if the thread is still active, reply with link
    else:
      link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
      embed = formatter.blank_embed(name, "Error", f"You already have an existing adventure. You cannot create more than one. Go to your editing thread to modify your adventure:\n{link}", "red")
      await ctx.reply(embed=embed)
      return
  #if no adventure found, create a new one
  else:
    # Create the adventure first
    database.create_blank_adventure(truename)
    # Then, create a new thread for editing this adventure
    database.pp("creating adventure edit channel:\n" + str(channel))
    if channel and channel.type == discord.ChannelType.text:
      thread = await channel.create_thread(name=f"{name} editing an adventure")
      await thread.send(ctx.author.mention + " is editing an adventure.")
      edit_thread_id = channel.id
        # Update the player's editthread field with the new thread ID
      database.update_player({'disc': truename, 'edit_thread_id': edit_thread_id})
      embed = formatter.blank_embed(name, "Success", f"Adventure was created and your edit thread is ready! Thread ID: {edit_thread_id}", "green")
      await ctx.reply(embed=embed, ephemeral=True)

async def setup(bot):
  bot.add_command(newadventure)