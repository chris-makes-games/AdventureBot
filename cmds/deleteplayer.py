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
    await ctx.send(f"ERROR: Player '{player_name}' not found.")
    return
  #allows players to delete themselves, bypasses permissions check
  if ctx.user.id == deletedplayer["disc"]:
    confirm = database.confirm_embed(confirm_text="This will delete all of your data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=ctx.channel, id=ctx.user.id)
    await ctx.reply(confirm, ephemral=True)
    return
  #if player is not trying to delete themselves, check permissions
  is_server_admin = permissions.is_admin(ctx)
  is_game_admin = permissions.is_maintainer(ctx)
  if not is_game_admin and not is_server_admin:
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
    print(f"User [{ctx.user.display_name}] tried to delete player [{player_name}] but does not have permission!")
    return
  else:
    player_id = deletedplayer["disc"]
    confirm = database.confirm_embed(confirm_text="This will delete all of " + player_name + "'s data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=ctx.channel, id=player_id)
    await ctx.response.send_message(confirm)
    return

# returns ten players that match the typing of the player name
@deleteplayer.autocomplete('player_name')
async def autocomplete_deleteplayer(ctx, current: str):
    players_query = database.get_all_players()
    possible_players = [player["displayname"] for player in players_query if current.lower() in player["displayname"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_players[:10]]