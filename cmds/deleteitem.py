import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#deletes an item from the database
@commands.hybrid_command(name="deleteitem", description="Delete an item by its ID")
async def deleteitem(ctx, item_id: str):
  item = database.testitems.find_one({"itemid": item_id})
  if not item:
    await ctx.reply("Error: Item not found! Double check your item ID!", ephemeral=True)
    return
  if ctx.author.id == item["author"] or permissions.is_maintainer:
    confirm = await database.confirm_embed(confirm_text=f"This will delete the item {item['name'].title()} permenantly, are you sure you want to do this?", title="Confirm Item Deletion", action="delete_item", channel=ctx.channel, id=item_id)
    embed = confirm[0]
    view = confirm[1]
    await ctx.reply(embed=embed, view=view, ephemeral=True)
  else:
    await ctx.reply("Error: You do not have permission to delete this item!", ephemeral=True)

@deleteitem.autocomplete('item_id')
async def autocomplete_item_id_deletion(interaction: discord.Interaction, current: str):
  #checks if author is maintainer, finds every room
  if database.check_permissions(interaction.user.id)[0]:
    item_ids_query = database.testitems.find(
  { 
  "itemid": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "itemid": 1,
  "_id": 0
  }
  )
    item_ids = [item["itemid"] for item in item_ids_query.limit(25)]
    return [app_commands.Choice(name=item_id, value=item_id) for item_id in item_ids]
  #if not maintainer, shows only their items
  else:
    item_ids_query = database.testitems.find(
  {
  "author": interaction.user.id, 
  "itemid": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "itemid": 1,
  "_id": 0
  }
  )
    item_ids = [item["itemid"] for item in item_ids_query.limit(25)]
    return [app_commands.Choice(name=item_id, value=item_id) for item_id in item_ids]

async def setup(bot):
  bot.add_command(deleteitem)