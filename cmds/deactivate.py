import discord
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
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
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
    print(e)

@deactivate.autocomplete("command")
async def autocomplete_reload(interaction: discord.Interaction, current: str):
  all_commands = database.get_all_commands()
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(deactivate)