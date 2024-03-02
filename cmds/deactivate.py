from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#adds a command to the deactivate list
#also unloads the command
#command will not load in on bot restart
@commands.hybrid_command(name="deactivate", description="deactivates and unloads a command")
async def deactivate(ctx, command: str):
  if not permissions.is_maintainer(ctx):
    await ctx.reply("You do not have permission to use this command.", ephemeral=True)
    return
  banned_commands = ["unload", "reload", "load", "deactivate", "activate"]
  if command.lower() in banned_commands:
    await ctx.reply("You cannot deactivate commands that load/unload!", ephemeral=True)
    return
  print(f"deactivating {command}...")
  try:
    await ctx.bot.unload_extension(f"cmds.{command.lower()}")
    database.deactivate_command(command)
    await ctx.reply(f"deactivated /{command} command", ephemeral=True)
    #sync was causing problems with autocompletion
    #await ctx.bot.tree.sync()
  except Exception as e:
    await ctx.reply(f"failed to unload {command}:\n{e}", ephemeral=True)

@deactivate.autocomplete("command")
async def autocomplete_reload(ctx, current: str):
  all_commands = database.get_all_commands()
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(deactivate)