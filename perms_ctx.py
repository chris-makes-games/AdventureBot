import discord

import database


#checks if the message is sent in a valid game thread
def correct_game_thread(ctx):
  player = database.get_player(ctx.author.id)
  if player is None:
    return False
  guild = player["guild"]
  thread = player["play_thread"]
  if guild != ctx.guild.id:
    return False
  if thread != ctx.channel.id:
    return False
  return True

#checks if the thread the player was in still exists
def thread_exists(ctx):
  player = database.get_player(ctx.author.id)
  if player is None:
    return False
  guild = player["guild"]
  if guild is None:
    return False
  thread = player["play_thread"]
  guild = ctx.bot.get_guild(guild)
  found_thread = guild.get_thread(thread)
  return bool(found_thread)

#checks for guild admin permissions
def is_admin(ctx):
  return ctx.author.guild_permissions.administrator

#checks guild owner permissions
def is_guild_owner(ctx):
  return ctx.author.id == ctx.guild.owner_id

#checks for a given role in the guild
#checks as is, lowercase, uppercase, and title case
def has_role(ctx, role_name):
  return discord.utils.get(ctx.author.roles, name=role_name) or discord.utils.get(ctx.author.roles, name=role_name.title()) or discord.utils.get(ctx.author.roles, name=role_name.upper()) or discord.utils.get(ctx.author.roles, name=role_name.lower())

#checks if the player is a bot maintainer
def is_maintainer(ctx):
  return database.check_permissions(ctx.author.id)[0]

#checks if the player is a bot maintainer's assistant
def is_assistant(ctx):
  return database.check_permissions(ctx.author.id)[1]

#checks for either assistant or maintainer permissions
def is_assistant_or_maintainer(ctx):
  return is_maintainer(ctx) or is_assistant(ctx)

#checks for any high-level guild/bot permissions
def check_any_admin(ctx):
  return is_admin(ctx) or is_guild_owner(ctx) or is_maintainer(ctx) or is_assistant(ctx)