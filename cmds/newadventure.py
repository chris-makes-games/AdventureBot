import formatter

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
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  #if the player already made an adventure
  if player["owned_adventures"]:
    embed = formatter.blank_embed(displayname, "Error", "You already have an adventure! You can only have one. Please use /editadventure to edit your adventure. You can also delete your adevnture with /deleteadventure.", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if they are in giantessworld, make sure they are an architect
  if ctx.guild.id == 730468423586414624 and not permissions.has_role(ctx, "architect"):
    embed = formatter.blank_embed(displayname, "Error", "You do not have permission to create an adventure. You need the architect role, please go to #role-select to get the role or contact Ironially-Tall", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if no adventure found, create a new one
  else:
    start_room = database.create_blank_room(truename)
    start = start_room.id
    name = name.lower()
    adventure = Adventure(name=name, start=start, rooms=[start], description=description, epilogue=epilogue, author=truename)
    database.adventures.insert_one(adventure.__dict__)
    #Update the player's editthread field with the new thread ID
    database.update_player({'disc': truename, 'owned_adventures': [name]})
    embed = formatter.blank_embed(displayname, "Success", f"Adventure {name.title()} was created! A default room with random ID `{start_room.id}` was generated as the start room for your adventure. Use `/editroom` to edit it or `/newroom` to add another.", "green")
    await ctx.reply(embed=embed, ephemeral=True)

async def setup(bot):
  bot.add_command(newadventure)