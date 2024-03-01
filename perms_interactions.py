import discord
from discord.webhook.async_ import interaction_message_response_params


def is_admin(interaction):
  return interaction.user.guild_permissions.administrator

def is_owner(interaction):
  return interaction.user.id == interaction.guild.owner_id

def has_role(interaction, role_name):
  return discord.utils.get(interaction.user.roles, name=role_name) is not None