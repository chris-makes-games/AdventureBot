import discord
from discord.ext import commands

import database
import perms_ctx as permissions
from player import Player


#creates a new player and adds them to the database
@commands.hybrid_command(name="newplayer", description="Create a new player")
async def newplayer(ctx, user: discord.User):
  player_id = ctx.author.id
  guild = ctx.guild.id
  same_player = player_id == user.id
  if not same_player and not permissions.is_assistant_or_maintainer:
    await ctx.repl("You must be a bot admin to add someone else as a player! Try adding yourself instead.")
    return
  player = database.get_player(user.id)
  if player and player["guild"] != guild:
    old_guild = ctx.client.get_guild(player["guild"])
    if old_guild:
      player = Player(discord=user.id, displayname=user.display_name, room=None, guild=guild)
      confirm = await database.confirm_embed(confirm_text=f"That user is already a player in another server! Do you want to start fresh in this server? Click below to overwrite the player data. This will delete the player data from the following server:\n{old_guild.name}", action="overwrite_player", channel=ctx.channel.id, title="Overwrite Player Data?", dict=player.__dict__)
      embed = confirm[0]
      view = confirm[1]
      await ctx.send(embed=embed, view=view, ephemeral=True)
      return
    else:
      await ctx.reply(f"It seems that player was playing in a server that no longer exists.\nServer ID:\n{player['guild']}\nDeleting player data...", ephemeral=True)
  if player and same_player:
    await ctx.reply(f"{ctx.author.mention} You are already a player! Use /join to start an adventure", ephemeral=True)
    return
  elif player and not same_player:
    await ctx.reply(f"{ctx.author.mention}, {user.name} is already a player!", ephemeral=True)
    return
  player = Player(discord=user.id, displayname=user.display_name, guild=guild, room=None, architect=False)
  database.new_player(player.__dict__)
  if same_player:
    await ctx.reply(f"{ctx.author.mention}, You are now a player! You can /join an adventure now. Try /adventures to see the list of available adventures. You can also use /help for a list of commands. Contact a moderator if you have any questions.", ephemeral=True)
  else:
    await ctx.reply(f"{ctx.author.mention} , {user.mention} is now a player!", ephemeral=True)


async def setup(bot):
  bot.add_command(newplayer)