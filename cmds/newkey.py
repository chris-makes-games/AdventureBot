import re

import discord
from discord import app_commands
from discord.ext import commands

import database
from key import Key


#edits a key with whatever the user selects
@commands.hybrid_command(name="newkey", description="Edit key attributes. Leave options blank to keep the default value.")
@app_commands.describe(
displayname="The name of the key, for inventory/journal purposes",
description="The description of an item, for inventory purposes only",
note="The text as it appears in the journal to players",
alt_note="For follow-up journal entries after the key is removed",
subkey1="A key that can be combined with other subkeys to make this key",
subkey2="A key that can be combined with other subkeys to make this key",
subkey3="A key that can be combined with other subkeys to make this key",
subkey4="A key that can be combined with other subkeys to make this key",
deconstruct="Whether the key can be turned into its subkeys with /deconstruct",
inventory="Whether the key will appear in an inventory",
journal="Whether the key will appear in a journal",
unique="If they player adds this to their inventory, they may not do so again",
repeating="Every time the player enters the room, the room will try to give them the key",
stackable="Whether The player may have more than one.")
async def newkey(ctx,
    #giant block of arguments!
    displayname : str="Default Key Name",
    description : str="Default Description",
    note : str | None=None,
    alt_note : str | None=None,
    subkey1 : str | None = None,
    subkey2 : str | None = None,
    subkey3 : str | None = None,
    subkey4 : str | None = None,
    inventory : bool | None = None,
    journal : bool | None = None,
    deconstruct : bool | None = None,
    unique : bool | None = None,
    repeating : bool | None = None,
    stackable : bool | None = None,
                  ):
  #generates a list of Keys by ID
  subkeys = []
  if subkey1 or subkey2 or subkey3 or subkey4:
    for subkey in [subkey1, subkey2, subkey3, subkey4]:
      if subkey: 
        subkeys.append(subkey[:4])
        

  #checks if the user is trying to edit a key that doesn't exist
  key_query = database.keys.find_one({"id": id})
  if key_query is None:
    await ctx.send(f"Key {id} does not exist. You should select a key from the drop-down menu.", ephemeral=True)
    return

#checks if the user is trying to edit a key that is already in use
  if subkeys:
    for subkey in subkeys:
      if database.keys.find_one({"displayname": subkey}) is not None:
        await ctx.send("Subkey already in use.")
        return

#tries to create a key object from all the data
#if it fails for any reason, sends the error
  try:
    new_key = Key(displayname=displayname, description=description,
note=note if note else None,
alt_note=alt_note if alt_note else None,  
subkeys=subkeys if subkeys else None, 
inventory=inventory if inventory else False, 
journal=journal if journal else False,
deconstruct=deconstruct if deconstruct else False,
unique=unique if unique else False, 
repeating=repeating if repeating else False, 
stackable=stackable if stackable else False)
  except Exception as e:
    await ctx.reply(f"There was a problem generating your key object. Did you enter in the data correctly? Error:\n{e}", ephemeral=True)
    return
  dict = new_key.__dict__
  embed = discord.Embed(title=f"New key: {dict['displayname']}", description=f"ID: {dict['id']} (automatically generated)\nReview the new key and select a button below. Any attribute not listed have been left at their default blank/False values.")
  embed.add_field(name="Displayname", value=f"{displayname}", inline=False)
  if dict['description']:
    embed.add_field(name="Description", value=f"{description}", inline=False)
  if dict['note']:
    embed.add_field(name="Note", value=f"{note}", inline=False)
  if dict['alt_note']:
    embed.add_field(name="Alt_Note", value=f"{alt_note}", inline=False)
  if dict['subkeys']:
    embed.add_field(name="Subkeys", value=f"{subkeys}", inline=False)
  if dict['inventory']:
    embed.add_field(name="Inventory", value=f"{inventory}", inline=False)
  if dict['journal']:
    embed.add_field(name="Journal", value=f"{journal}", inline=False)
  if dict['unique']:
    embed.add_field(name="Unique", value=f"{unique}", inline=False)
  if dict['repeating']:
    embed.add_field(name="Repeating", value=f"{repeating}", inline=False)
  if dict['stackable']:
    embed.add_field(name="Stackable", value=f"{stackable}", inline=False)
  
  edit_button = database.ConfirmButton(label="Create Key", confirm=True, action="new_key", id=id, dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)


#autocompletes the IDs of available keys for subkeys
@newkey.autocomplete('subkey1')
async def autocomplete_subkey1(interaction: discord.Interaction, current: str):
  key_query = database.keys.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  key_info = [(key["id"], key["displayname"]) for key in key_query]
  choices = [app_commands.Choice(name=f"{key_id} - {displayname}", value=key_id) for key_id, displayname in key_info[:25]]
  return choices

#autocompletes the IDs of available keys for subkeys
@newkey.autocomplete('subkey2')
async def autocomplete_subkey2(interaction: discord.Interaction, current: str):
  key_query = database.keys.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  key_info = [(key["id"], key["displayname"]) for key in key_query]
  choices = [app_commands.Choice(name=f"{id} - {displayname}", value=key_id) for key_id, displayname in key_info[:25]]
  return choices

#autocompletes the IDs of available keys for subkeys
@newkey.autocomplete('subkey3')
async def autocomplete_subkey3(interaction: discord.Interaction, current: str):
  key_query = database.keys.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  key_info = [(key["id"], key["displayname"]) for key in key_query]
  choices = [app_commands.Choice(name=f"{key_id} - {displayname}", value=key_id) for key_id, displayname in key_info[:25]]
  return choices

#autocompletes the IDs of available keys for subkeys
@newkey.autocomplete('subkey4')
async def autocomplete_subkey4(interaction: discord.Interaction, current: str):
  key_query = database.keys.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  key_info = [(key["id"], key["displayname"]) for key in key_query]
  choices = [app_commands.Choice(name=f"{key_id} - {displayname}", value=key_id) for key_id, displayname in key_info[:25]]
  return choices
  

async def setup(bot):
  bot.add_command(newkey)