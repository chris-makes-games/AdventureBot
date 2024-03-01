import discord


def is_admin(ctx):
  return ctx.author.guild_permissions.administrator

def is_owner(ctx):
  return ctx.author.id == ctx.guild.owner_id

def has_role(ctx, role_name):
  return discord.utils.get(ctx.author.roles, name=role_name) is not None