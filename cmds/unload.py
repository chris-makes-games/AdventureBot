import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#unloads a command
#command will stop working until reloaded
@commands.hybrid_command(name="unload", description="unloads a command")
async def unload(ctx, command: str):
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
    await ctx.reply("You cannot unload commands that load/unload!", ephemeral=True)
    return
  print(f"unloading {command}")
  try:
    await ctx.bot.unload_extension(f"cmds.{command.lower()}")
    await ctx.reply(f"unloaded /{command} command", ephemeral=True)
    #sync was causing problems with autocompletion
    #await ctx.bot.tree.sync()
  except Exception as e:
    await ctx.reply(f"failed to unload {command}:\n{e}", ephemeral=True)
    print(e)

@unload.autocomplete("command")
async def autocomplete_reload(interaction : discord.Interaction, current: str):
  all_commands = database.get_all_commands()
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(unload)