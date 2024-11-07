import discord
from discord import app_commands
from discord.ext import commands

import database
from key import Key

import perms_interactions as perms

import re


#edits a key with whatever the user selects
@commands.hybrid_command(name="newkey", description="Edit key attributes. Leave options blank to keep the default value.")
@app_commands.describe(
adventure = "The adventure this key will belong to",
id = "Optionally input your own unique ID, must be unique across ALL player IDs!",
displayname="The name of the key, for inventory/journal purposes",
description="The description of an item, for inventory purposes only",
note="The text as it appears in the journal to players",
alt_note="For follow-up journal entry created after this key is removed from the player",
subkeys="Keys that can be crafted together make this key. Can be multiple. Separate by commas",
deconstruct="Whether this key can be turned into its subkeys by deconstructing",
combine="Whether this key can be combined with other keys",
inventory="Whether this key will appear in the player's inventory",
journal="Whether this key will appear in the player's journal",
unique="If they player adds this to their inventory, they may not do so again",
repeating="Every time the player enters the room, the room will try to give them the key",
stackable="Whether The player may have more than one.")
async def newkey(ctx,
    #giant block of arguments!
    adventure,
    id : str | None = None,
    displayname : str="Default Key Name",
    description : str="Default Description",
    note : str | None=None,
    alt_note : str | None=None,
    subkeys : str | None = None,
    deconstruct : bool | None = None,
    combine : bool | None = None,
    inventory : bool | None = None,
    journal : bool | None = None,
    unique : bool | None = None,
    repeating : bool | None = None,
    stackable : bool | None = None,
                  ):
#checks if player exists in the database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer before trying to make a new room.", ephemeral=True)
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
  
  #adds the adventure name to the room
  found_adventure = database.get_adventure(adventure.lower())
  if not found_adventure:
    await ctx.reply(f"ERROR: The adventure {adventure} does not exist. You should choose your adventure from the drop-down menu!", ephemeral=True)
    return
  else:
    adventure_of_key = found_adventure["name"].title()

  errors = []

  warnings = []
  
  #checks if user input valid unique ID
  if id:
    new_id = id
    found_id = database.get_id(id)
    if found_id:
      new_id = database.generate_unique_id()
      warnings.append(f"ID `{found_id['id']}` already exists from author {found_id['author']}. A random ID was generated instead: `{new_id}`")
    elif id == "none" or id == "None":
      new_id = database.generate_unique_id()
      warnings.append(f"Key must have an ID. Random ID generated: `{new_id}`")
    elif id and id.isdigit():
      new_id = database.generate_unique_id()
      warnings.append(f"Key ID cannot be only numbers. Random ID generated instead: `{new_id}`")
  else:
    #if no ID, generates a random one
    new_id = database.generate_unique_id()
    warnings.append(f"Random ID generated for key: `{new_id}`")

  #parses subkeys into dict
  subkeys_string = ""
  new_subkeys = {}
  if subkeys:
    pairs = subkeys.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_subkeys[item.strip()] = int(quantity)
      except ValueError:
        errors.append(f"Invalid subkey format: {pair}`\n(must be in the format `key_id <number>`)")
        continue
      if not database.get_key(item.strip()):
        warnings.append(f"Key `{item.strip()}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
    #parses subkeys into neat string
  if new_subkeys:
    for key in new_subkeys:
      subkeys_string += f"{key} x{new_subkeys[key]}\n"
  else:
    subkeys = None

  #turns errors into string, removes duplicates
  error_title = ""
  if errors:
    parsed_errors = []
    for error in errors:
      if error not in parsed_errors:
        parsed_errors.append(error)
    if len(parsed_errors) > 1:
      error_title = "**ERRORS**"
    else:
      error_title = "**ERROR**"
    parsed_errors = "\n- ".join(parsed_errors)
    errors = parsed_errors

  #turns warnings into string, removes duplicates
  warn_title = ""
  if warnings:
    parsed_warnings = []
    for warning in warnings:
      if warning not in parsed_warnings:
        parsed_warnings.append(warning)
    if len(parsed_warnings) > 1:
      warn_title = "**WARNINGS**"
    else:
      warn_title = "**WARNING**"
    parsed_warnings = "\n- ".join(parsed_warnings)
    warnings = parsed_warnings

#tries to create a key object from all the data
#if it fails for any reason, sends the error
  try:
    new_key = Key(
adventure=adventure_of_key,
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
    print(e)
    return
  dict = new_key.__dict__
  embed = discord.Embed(title=f"New key: {dict['displayname']}", description=f"**ID: `{dict['id']}`** \nReview the new key and select a button below. Any attribute not listed have been left at their default blank/False values.")
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
    embed.add_field(name=warn_title, value=warnings)
  if errors:
    embed.add_field(name=error_title, value=warnings)
  
  edit_button = database.ConfirmButton(label="Create Key", confirm=True, action="new_key", id=id, dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

  #returns adventures either owned or coauthored with matching name
@newkey.autocomplete('adventure')
async def autocomplete_newkey(interaction: discord.Interaction, current: str):
  if perms.is_assistant_or_maintainer(interaction):
    adventure_query = database.adventures.find(
      {"name": {"$regex": re.escape(current), "$options": "i"}},
      {"name": 1, "author": 1, "_id": 0}
      )
  else:
    adventure_query = database.adventures.find({
    "$or": [
      {"author": interaction.user.id},  # Owned by the user
      {"coauthors": interaction.user.id}  # Coauthored by the user
      ],
    "name": {"$regex": re.escape(current), "$options": "i"}
      },
    {"name": 1, "author": 1, "_id": 0}
    )
  adventure_info = [(adventure["name"].title(), adventure["author"]) for adventure in adventure_query]
  choices = [app_commands.Choice(name=f"{name.title()}", value=name.title()) for name, author in adventure_info[:25]]
  return choices
  

async def setup(bot):
  bot.add_command(newkey)