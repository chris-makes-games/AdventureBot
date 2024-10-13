import discord

import database


#checks if the message is being sent in a thread that belongs to the player sending the message
def thread_check(interaction):
  player = database.get_player(interaction.user.id)
  return player and interaction.channel.id in player["play_thread"]

#checks for guild admin permissions
def is_admin(interaction):
  return interaction.user.guild_permissions.administrator

#checks guild owner permissions
def is_guild_owner(interaction):
  return interaction.user.id == interaction.guild.owner_id
  
#checks for a given role in the guild
def has_role(interaction, role_name):
  return discord.utils.get(interaction.user.roles, name=role_name) is not None

#checks if the player is a bot maintainer
def is_maintainer(interaction):
  return database.check_permissions(interaction.user.id)[0]

#checks if the player is a bot maintainer's assistant
def is_assistant(interaction):
  return database.check_permissions(interaction.user.id)[1]

#checks for either assistant or maintainer permissions
def is_assistant_or_maintainer(interaction):
  return is_maintainer(interaction) or is_assistant(interaction)

#checks for any high-level guild/bot permissions
def check_all(interaction):
  return is_admin(interaction) or is_guild_owner(interaction) or is_maintainer(interaction) or is_assistant(interaction)