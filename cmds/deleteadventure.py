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
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return
  adventure = database.adventures.find_one({"name": adventure_name})
  if not adventure:
    await ctx.reply("Error: Adventure not found! Double check your Advenutre name!", ephemeral=True)
    # Check if the room belongs to the user
    # if not, then check for maintainer
  if ctx.author.id == adventure["author"] or permissions.is_maintainer(ctx):
    confirm = await database.confirm_embed(confirm_text=f"This will delete the adventure **{adventure['name'].title()}** permenantly, are you sure you want to do this?", title="Confirm Adventure Deletion", action="delete_adventure", channel=ctx.channel, id=adventure_name)
    embed = confirm[0]
    view = confirm[1]
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