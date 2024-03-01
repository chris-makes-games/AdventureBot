import discord

import database


def is_admin(interaction):
  return interaction.user.guild_permissions.administrator

def is_owner(interaction):
  return interaction.user.id == interaction.guild.owner_id

def has_role(interaction, role_name):
  return discord.utils.get(interaction.user.roles, name=role_name) is not None

def is_maintainer(interaction):
  return database.check_permissions(interaction.user.id)[0]

def is_assistant(interaction):
  return database.check_permissions(interaction.user.id)[1]

def check_all(interaction):
  return is_admin(interaction) or is_owner(interaction) or is_maintainer(interaction) or is_assistant(interaction)