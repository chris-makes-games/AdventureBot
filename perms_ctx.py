import discord

import database


#checks if the message is sent in a valid game thread
def correct_game_thread(ctx):
  player = database.get_player(ctx.author.id)
  if player is None:
    return False
  guild_thread = player["guild_thread"]
  if ctx.channel.id in guild_thread and ctx.guild.id in guild_thread:
      return True
  return False

#checks if the message is sent in a valid edit thread
def correct_edit_thread(ctx):
  player = database.get_player(ctx.author.id)
  if player is None:
    return False
  edit_thread = player["edit_thread"]
  if ctx.channel.id == edit_thread:
      return True
  return False

#checks if the thread the player was in still exists
def thread_exists(ctx):
  player = database.get_player(ctx.author.id)
  if player is None:
    return False
  guild_thread = player["guild_thread"]
  if player is None:
    return False
  if guild_thread is None:
    return False
  guild = ctx.bot.get_guild(guild_thread[0])
  thread = guild.get_thread(guild_thread[1])
  if thread:
    return True
  return False

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