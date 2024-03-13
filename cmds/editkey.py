import re

import discord
from discord import app_commands
from discord.ext import commands

import database


#edits a key with whatever the user selects
@commands.hybrid_command(name="editkey", description="Edit key attributes. Leave options blank to keep the current value")
async def editkey(ctx, id: str,
    #giant block of optional arguments!
    description : str | None = None,
    displayname : str | None = None,
    subkeys : str | None = None,
    inventory : bool | None = None,
    journal : bool | None = None,
    unique : bool | None = None,
    repeating : bool | None = None,
    stackable : bool | None = None,
                  ):
  found_key = database.keys.find_one({"id": id})
  if not found_key:
    await ctx.reply(f"Error: No key found with id **{id}**! Double check you've selected a valid key. If you need to make a new key, try /newkey", ephemeral=True)
    return
  new_dict = found_key.copy()
  embed = discord.Embed(title=f"Editing key: {found_key['displayname']}\nID: **{id}**", description="Review the changes and select a button below:")
  if description:
    new_dict["description"] = description
    embed.add_field(name="Description", value=f"Old: {found_key['description']}\nNew: {description}", inline=False)
  if displayname:
    new_dict["displayname"] = displayname
    embed.add_field(name="Displayname", value=f"Old: {found_key['displayname']}\nNew: {displayname}", inline=False)
  if subkeys:
    new_dict["subkeys"] = subkeys
    embed.add_field(name="Subkeys", value=f"Old: {found_key['subkeys']}\nNew: {subkeys}", inline=False)
  if inventory:
    new_dict["inventory"] = inventory
    embed.add_field(name="Inventory", value=f"Old: {found_key['inventory']}\nNew: {inventory}", inline=False)
  if journal:
    new_dict["journal"] = journal
    embed.add_field(name="Journal", value=f"Old: {found_key['journal']}\nNew: {journal}", inline=False)
  if unique:
    new_dict["unique"] = unique
    embed.add_field(name="Unique", value=f"Old: {found_key['unique']}\nNew: {unique}", inline=False)
  if repeating:
    new_dict["repeating"] = repeating
    embed.add_field(name="Repeating", value=f"Old: {found_key['repeating']}\nNew: {repeating}", inline=False)
  if stackable:
    new_dict["stackable"] = stackable
    embed.add_field(name="Stackable", value=f"Old: {found_key['stackable']}\nNew: {stackable}", inline=False)
  
  if not embed.fields:
    embed.description = "ERROR"
    embed.add_field(name="No changes", value="No changes were made. You need to select one of the options to edit the key. If you're unsure, try /help editkey")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  edit_button = database.ConfirmButton(label="Make Changes", confirm=True, action="edit_key", id=id, dict=new_dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

#returns keys with matching id OR matching displayname
@editkey.autocomplete('id')
async def autocomplete_editkey(interaction: discord.Interaction, current: str):
  key_query = database.keys.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  key_info = [(key["id"], key["displayname"]) for key in key_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in key_info[:25]]
  return choices

async def setup(bot):
  bot.add_command(editkey)