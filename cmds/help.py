import discord
from discord import app_commands
from discord.ext import commands

import database
import formatter


#basic help command, replies with embed
#allows the user to optionally !help other commands
#will only autocomplete with commands that the user has permission to use
@commands.hybrid_command()
async def help(ctx, command=None):
  await ctx.reply(embed=formatter.help(command), ephemeral=True)

@help.autocomplete("command")
async def autocomplete_help(interaction: discord.Interaction, current: str):
  if database.check_permissions(interaction.user.id)[0]:
    all_commands = database.get_all_commands()
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