import discord
from discord.ext import commands

import database
import perms_ctx as permissions
from player import Player


#creates a new player and adds them to the database
@commands.hybrid_command(name="newplayer", description="Create a new player")
async def newplayer(ctx, user: discord.User):
  player_id = ctx.author.id
  same_player = player_id == user.id
  if not same_player and not permissions.is_maintainer:
    await ctx.repl("You must be a bot maintainer to add someone else as a player! Try adding yourself instead.")
  player = database.get_player(user.id)
  if player and same_player:
    await ctx.reply(f"{ctx.author.mention} You are already a player!", ephemeral=True)
    return
  elif player and not same_player:
    await ctx.reply(f"{ctx.author.mention}, {user.name} is already a player!", ephemeral=True)
    return
  player = Player(discord=user.id, displayname=user.display_name, room=None, inventory=[], taken=[], architect=False)
  database.new_player(player.__dict__)
  if same_player:
    await ctx.reply(f"{ctx.author.mention} , You are now a player! You can /join an adventure now. Try /adventures to see the list of available adventures.", ephemeral=True)
  else:
    await ctx.reply(f"{ctx.author.mention} , {user.mention} is now a player!", ephemeral=True)

async def setup(bot):
  bot.add_command(newplayer)