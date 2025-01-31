import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#removes a command from the deactivate list
#also loads the command
#bot might need a restart to get slash commands working again
#command will at least work as a regular (not slash) command)
@commands.hybrid_command(name="activate", description="activates and loads a command")
async def activate(ctx, command: str):
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
  if not database.botinfo.find_one({"inactive": command}):
    await ctx.reply("That command is already active.", ephemeral=True)
    return
  print(f"activating {command}...")
  try:
    await ctx.bot.load_extension(f"cmds.{command.lower()}")
    database.activate_command(command)
    await ctx.reply(f"activated /{command} command", ephemeral=True)
    #sync was causing problems with autocompletion
    #await ctx.bot.tree.sync()
  except Exception as e:
    await ctx.reply(f"failed to activate {command}:\n{e}", ephemeral=True)
    print(e)

@activate.autocomplete("command")
async def autocomplete_activate(interaction: discord.Interaction, current: str):
  all_commands = database.get_all_commands()
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(activate)