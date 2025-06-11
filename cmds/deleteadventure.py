import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes a single adveture from the database
#notably does not delete the rooms in the adventure
@commands.hybrid_command(name="deleteadventure", description="Deletes an adventure by its name")
async def deleteadventure(ctx, adventure_name: str):
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
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
  adventure = database.adventures.find_one({"name": adventure_name})
  if not adventure:
    await ctx.reply("Error: Adventure not found! Double check your Advenutre name!", ephemeral=True)
    # Check if the room belongs to the user
    # if not, then check for maintainer
  if ctx.author.id == adventure["author"] or permissions.is_maintainer(ctx):
    confirm = await database.confirm_embed(ctx.interaction.id, confirm_text=f"This will delete the adventure `{adventure['name'].title()}` **PERMENANTLY**, are you sure you want to do this? This will also delete every room in the adventure! This cannot be undone!", title="Confirm Adventure Deletion", action="delete_adventure", channel=ctx.channel, id=adventure_name)
    embed = confirm[0]
    view = confirm[1]
    affected_rooms = ", ".join(adventure["rooms"])
    embed.add_field(name="Affected Rooms", value=f"These rooms will be deleted: {affected_rooms}")
    affected_keys = []
    found_keys = database.keys.find({"adventure" : adventure["name"]})
    if found_keys:
      for key in found_keys:
        affected_keys.append(key["id"])
      affected_keys = ", ".join(affected_keys)
    if affected_keys:
      embed.add_field(name="Affected Keys", value=f"These keys will also be deleted: {affected_keys}")
    affected_players = database.get_players_in_adventure(adventure["name"])
    if affected_players:
      affected_players = ", ".join(affected_players)
      embed.add_field(name="Affected Players", value=f"These players will be kicked from their adventure: {affected_players}")
    await ctx.reply(embed=embed, view=view, ephemeral=True)
  else:
    await ctx.reply("Error: You do not have permission to delete this room!", ephemeral=True)


@deleteadventure.autocomplete('adventure_name')
async def autocomplete_adventure_deletion(interaction: discord.Interaction, current: str):
  #checks if author is maintainer, finds every room
  if database.check_permissions(interaction.user.id)[0]:
    advs_query = database.adventures.find(
  {
  "name": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "name": 1, 
  "_id": 0
  }
  )
    adventure_ids = [adv["name"] for adv in advs_query.limit(25)]
    return [app_commands.Choice(name=adv_id, value=adv_id) for adv_id in adventure_ids]
  else:
    #if not maintainer, shows only their rooms
    advs_query = database.adventures.find(
  {
  "name": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "author": interaction.user.id,
  "name": 1, 
  "_id": 0
  }
  )
    adventure_ids = [adv["name"] for adv in advs_query.limit(25)]
    return [app_commands.Choice(name=adv_id, value=adv_id) for adv_id in adventure_ids]

  
async def setup(bot):
  bot.add_command(deleteadventure)