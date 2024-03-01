import discord

import database


def is_admin(ctx):
  return ctx.author.guild_permissions.administrator

def is_owner(ctx):
  return ctx.author.id == ctx.guild.owner_id

def has_role(ctx, role_name):
  return discord.utils.get(ctx.author.roles, name=role_name) is not None

def is_maintainer(ctx):
  return database.check_permissions(ctx.author.id)[0]

def is_assistant(ctx):
  return database.check_permissions(ctx.author.id)[1]

def is_assistant_or_maintainer(ctx):
  return is_maintainer(ctx) or is_assistant(ctx)

def check_all(ctx):
  return is_admin(ctx) or is_owner(ctx) or is_maintainer(ctx) or is_assistant(ctx)