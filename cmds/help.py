import formatter

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_interactions as permissions


#basic help command, replies with embed
#allows the user to optionally /help other commands
#will only autocomplete with commands that the user has permission to use
@commands.hybrid_command()
async def help(ctx, command=None):
  await ctx.reply(embed=formatter.help(command), ephemeral=True)
  return

@help.autocomplete("command")
async def autocomplete_help(interaction: discord.Interaction, current: str):
  if permissions.is_maintainer(interaction):
    all_commands = database.get_all_commands()
    choices = []
    for cmd in all_commands:
      if current.lower() in cmd.lower():
        choices.append(app_commands.Choice(name=cmd, value=cmd))
    return choices
  elif permissions.has_role(interaction, "architect"):
    all_commands = database.get_architect_commands()
    choices = []
    for cmd in all_commands:
      if current.lower() in cmd.lower():
        choices.append(app_commands.Choice(name=cmd, value=cmd))
    return choices
  else:
    all_commands = database.get_player_commands()
    choices = []
    for cmd in all_commands:
      if current.lower() in cmd.lower():
        choices.append(app_commands.Choice(name=cmd, value=cmd))
    return choices

async def setup(bot):
  bot.add_command(help)