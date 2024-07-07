import discord
from discord import app_commands
from discord.ext import commands

import database
from key import Key


#edits a key with whatever the user selects
@commands.hybrid_command(name="newkey", description="Edit key attributes. Leave options blank to keep the default value.")
@app_commands.describe(
id = "Optionally input your own unique ID, must be unique across ALL player IDs!",
displayname="The name of the key, for inventory/journal purposes",
description="The description of an item, for inventory purposes only",
note="The text as it appears in the journal to players",
alt_note="For follow-up journal entry created after this key is removed from the player",
subkeys="Keys that can be crafted together make this key. Can be multiple. Separate by commas",
deconstruct="Whether this key can be turned into its subkeys by deconstructing",
unique="If they player adds this to their inventory, they may not do so again",
repeating="Every time the player enters the room, the room will try to give them the key",
stackable="Whether The player may have more than one.")
async def newkey(ctx,
    #giant block of arguments!
    id : str | None = None,
    displayname : str="Default Key Name",
    description : str="Default Description",
    note : str | None=None,
    alt_note : str | None=None,
    subkeys : str | None = None,
    deconstruct : bool | None = None,
    unique : bool | None = None,
    repeating : bool | None = None,
    stackable : bool | None = None,
                  ):
#checks if player exists in the database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer before trying to make a new room.", ephemeral=True)
    return

  warnings = []
  
  #checks if user input valid unique ID
  if id and database.get_id(id):
    found_id = database.get_id(id)
    await ctx.reply(f"ERROR: ID already exists. Please use a different ID.\n**ID:** {id}\nID **Author:** {found_id['author']}", ephemeral=True)
    return

  #if no ID, generates a random one
  new_id = id if id else database.generate_unique_id()

  #parses subkeys into dict
  subkeys_string = ""
  new_subkeys = {}
  if subkeys:
    pairs = subkeys.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_subkeys[item.strip()] = int(quantity)
        if not database.get_key(item.strip()):
          warnings.append(f"Key {item.strip()} does not exist. Did you enter the ID wrong or are you planning to create one later?")
      except ValueError:
        await ctx.reply("Invalid subkey format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the subkeys to one of somekey and three of otherkey)", ephemeral=True)
    #parses subkeys into neat string
    for key in new_subkeys:
      subkeys_string += f"{key} x{new_subkeys[key]}\n"

  #turns list of warnings to a string
  if warnings:
    warnings = "\n".join(warnings)

#tries to create a key object from all the data
#if it fails for any reason, sends the error
  try:
    new_key = Key(
id = new_id,
displayname=displayname, 
description=description,
note=note if note else None,
alt_note=alt_note if alt_note else None,  
subkeys=new_subkeys, 
deconstruct=deconstruct if deconstruct else False,
unique=unique if unique else False, 
repeating=repeating if repeating else False, 
stackable=stackable if stackable else False,
author = ctx.author.id)
  except Exception as e:
    await ctx.reply(f"There was a problem generating your key object. Did you enter in the data correctly? Error:\n{e}", ephemeral=True)
    return
  dict = new_key.__dict__
  embed = discord.Embed(title=f"New key: {dict['displayname']}", description=f"ID: {dict['id']} \nReview the new key and select a button below. Any attribute not listed have been left at their default blank/False values.")
  embed.add_field(name="Displayname", value=f"{displayname}", inline=False)
  if dict['description']:
    embed.add_field(name="Description", value=f"{description}", inline=False)
  if dict['note']:
    embed.add_field(name="Note", value=f"{note}", inline=False)
  if dict['alt_note']:
    embed.add_field(name="Alt_Note", value=f"{alt_note}", inline=False)
  if dict['subkeys']:
    embed.add_field(name="Subkeys", value=subkeys_string, inline=False)
  if dict['unique']:
    embed.add_field(name="Unique", value=f"{unique}", inline=False)
  if dict['repeating']:
    embed.add_field(name="Repeating", value=f"{repeating}", inline=False)
  if dict['stackable']:
    embed.add_field(name="Stackable", value=f"{stackable}", inline=False)
  if warnings:
    embed.add_field(name="**WARNING:**", value=warnings)
  
  edit_button = database.ConfirmButton(label="Create Key", confirm=True, action="new_key", id=id, dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)
  

async def setup(bot):
  bot.add_command(newkey)