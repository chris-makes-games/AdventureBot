import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes an key from the database
@commands.hybrid_command(name="deletekey", description="Delete an key by its ID")
async def deletekey(ctx, id: str):
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return
  key = database.keys.find_one({"id": id})
  if not key:
    await ctx.reply("Error: Item not found! Double check your key ID!", ephemeral=True)
    return
  if ctx.author.id == key["author"] or permissions.check_any_admin:
    confirm = await database.confirm_embed(confirm_text=f"This will delete the key {key['displayname'].title()} permenantly, are you sure you want to do this? Key will also be removed from all rooms where it appears, and removed from all players currently holding one.\n**THIS CANNOT BE UNDONE!**", title="Confirm Item Deletion", action="delete_key", channel=ctx.channel, id=id)
    embed = confirm[0]
    view = confirm[1]
    await ctx.reply(embed=embed, view=view, ephemeral=True)
  else:
    await ctx.reply("Error: You do not have permission to delete this key!", ephemeral=True)

@deletekey.autocomplete('id')
async def autocomplete_id_deletion(interaction: discord.Interaction, current: str):
  #checks if author is maintainer, finds every room
  if database.check_permissions(interaction.user.id)[0]:
    ids_query = database.keys.find(
  { 
  "id": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "id": 1,
  "_id": 0
  }
  )
    ids = [key["id"] for key in ids_query.limit(25)]
    return [app_commands.Choice(name=id, value=id) for id in ids]
  #if not maintainer, shows only their keys
  else:
    ids_query = database.keys.find(
  {
  "author": interaction.user.id, 
  "id": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "id": 1,
  "_id": 0
  }
  )
    ids = [key["id"] for key in ids_query.limit(25)]
    return [app_commands.Choice(name=id, value=id) for id in ids]

async def setup(bot):
  bot.add_command(deletekey)