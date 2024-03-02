#WIP

from discord.ext import commands
from discord import app_commands
import database


#deletes a player from the database
#uses displayname of player to search
#admins can delete any player, players can delete themselves
@commands.hybrid_command(name="deleteplayer", description="Delete a player")
async def deleteplayer(ctx, player_name: str):
  player_id = interaction.user.id
  guild = interaction.guild
  if not guild:
    return
  guild_member = guild.get_member(player_id)
  if not guild_member:
    return
  #allows players to delete themselves, bypasses permissions check
  if player_name == guild_member.display_name:
    confirm = database.confirm_embed(confirm_text="This will delete all of your data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=interaction.channel, id=interaction.user.id)
    await interaction.response.send_message(confirm)
    return
  #if player is not trying to delete themselves, check permissions
  permissions = guild_member.guild_permissions
  is_server_admin = permissions.administrator
  is_game_admin = database.get_player_info(player_id, "admin")
  if not is_game_admin and not is_server_admin:
    await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    print(f"User [{guild_member.display_name}] tried to delete player [{player_name}] but does not have permission!")
    return
  else:
    player_id = database.get_player_info_by_displayname(player_name, "disc")
    confirm = database.confirm_embed(confirm_text="This will delete all of " + player_name + "'s data, are you sure you want to do this?", title="Confirm Deletion", action="delete_player", channel=interaction.channel, id=player_id)
    await interaction.response.send_message(confirm)
    return

# Autocompletion function for adventure_name in join command
@deleteplayer.autocomplete('player_name')
async def autocomplete_deleteplayer(ctx, current: str):
#query the database for adventure names and filter based on the current input
    players_query = database.get_all_players()
    possible_players = [player["displayname"] for player in players_query if current.lower() in player["displayname"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_players[:25]]