import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes a player from the database
#uses displayname in databse of player to search
#admins can delete any player, players can delete themselves
@commands.hybrid_command(name="deleteplayer", description="Delete a player")
async def deleteplayer(ctx, player_name: str):
  deletedplayer = database.users.find_one({"displayname": player_name})
  #checks if player is in the database
  if not deletedplayer:
    await ctx.send(f"ERROR: Player '{player_name}' not found.", ephemeral=True)
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
    print(f"User [{ctx.author.display_name}] tried to delete player [{player_name}] but does not have permission!")
    return
  else:
  #send the confirmation embed with buttons to click
    confirm = await database.confirm_embed(confirm_text="This will delete all of " + player_name + "'s data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=ctx.channel, id=deletedplayer["disc"])
    embed = confirm[0]
    view = confirm[1]
    await ctx.send(embed=embed, view=view, ephemeral=True)
    return

# returns ten players that match the typing of the player name
@deleteplayer.autocomplete('player_name')
async def autocomplete_deleteplayer(interaction: discord.Interaction, current: str):
    players_query = database.get_all_players()
    possible_players = [player["displayname"] for player in players_query if current.lower() in player["displayname"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_players[:10]]

async def setup(bot):
  bot.add_command(deleteplayer)