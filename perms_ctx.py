import discord

import database


#checks if the message is being sent in a thread that belongs to the player sending the message
def thread_check(ctx):
  player = database.get_player(ctx.author.id)
  if player is None:
    return False
  print("threads: " + str(player["guilds_threads"]))
  return ctx.channel.id in player["guilds_threads"]

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