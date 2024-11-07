import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes a player from the database
#uses displayname in databse of player to search
#admins can delete any player, players can delete themselves
@commands.hybrid_command(name="deleteplayer", description="Delete a player")
async def deleteplayer(ctx, user: discord.User):
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
  deletedplayer = database.users.find_one({"disc": user.id})
  #checks if player is in the database
  if not deletedplayer:
    await ctx.send(f"ERROR: Player '{user.display_name}' not found.", ephemeral=True)
    return
  #allows players to delete themselves, bypasses permissions check
  if ctx.author.id == deletedplayer["disc"]:
    confirm = await database.confirm_embed(confirm_text="This will delete all of your data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=ctx.channel, id=ctx.author.id)
    embed = confirm[0]
    view = confirm[1]
    await ctx.send(embed=embed, view=view, ephemeral=True)
    return
  #if player is not trying to delete themselves, check permissions
  if not permissions.is_maintainer:
    await ctx.reply("You do not have permission to use this command. Contact a server admin or bot maintainer.", ephemeral=True)
    print(f"User [{ctx.author.display_name}] tried to delete player [{user.display_name}] but does not have permission!")
    return
  else:
  #send the confirmation embed with buttons to click
    confirm = await database.confirm_embed(confirm_text=f"This will delete all of {user.display_name}'s data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=ctx.channel, id=deletedplayer["disc"])
    embed = confirm[0]
    view = confirm[1]
    await ctx.send(embed=embed, view=view, ephemeral=True)
    return

async def setup(bot):
  bot.add_command(deleteplayer)