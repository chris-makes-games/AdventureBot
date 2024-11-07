import re

import discord
from discord import app_commands
from discord.ext import commands

import database


#edits a key with whatever the user selects
@commands.hybrid_command(name="editkey", description="Edit key attributes. Leave options blank to keep the current value")
@app_commands.describe(
new_id = "Change key ID. Changing this will automatically update all uses of the key",
displayname="The name of the key, for inventory/journal purposes",
description="The description of an item, for inventory purposes only",
note="The text as it appears in the journal to players",
alt_note="For follow-up journal entries after the key is removed",
subkeys="A key that can be combined with other subkeys to make this key",
deconstruct="Whether this key can be turned into its subkeys by deconstructing",
combine="Whether this key can be combined with other keys",
inventory="Whether this key will appear in the player's inventory",
journal="Whether this key will appear in the player's journal",
unique="If they player adds this to their inventory, they may not do so again",
repeating="Every time the player enters the room, the room will try to give them the key",
stackable="Whether The player may have more than one.")
async def editkey(ctx, id : str,
  #giant block of arguments!
  new_id : str | None = None,
  displayname : str | None = None,
  description : str | None = None,
  note : str | None = None,
  alt_note : str | None = None,
  subkeys : str | None = None,
  deconstruct : bool | None = None,
  combine : bool | None = None,
  inventory : bool | None = None,
  journal : bool | None = None,
  unique : bool | None = None,
  repeating : bool | None = None,
  stackable : bool | None = None,
                ):

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
 
  #errors for big issues
  errors = []

  #warnings for minor issues
  warnings = []

  #error for no key found
  found_key = database.keys.find_one({"id": id})
  if not found_key:
    await ctx.reply(f"Error: No key found with id **{id}**! Double check you've selected a valid key. If you need to make a new key, try /newkey", ephemeral=True)
    return

  #check for None assignment attempts in mandatory fields
  if new_id:
    if new_id.lower() == "none" or new_id.strip() == "":
      errors.append(f"You cannot change the ID of a key to blank! Key must have an ID. Key ID will remain `{id}`")
      new_id = None
    elif len(new_id) < 6:
      errors.append(f"Your ID must be at least six characters! Key ID will remain {id}")
      new_id = None
  if displayname:
    if displayname.lower() == "none" or displayname.strip() == "":
      errors.append(f"Display name cannot be blank! Key will keep display name of {found_key['displayname']}")
      displayname = None
  if description:
    if description.lower() == "none" or description.strip() == "":
      errors.append(f"Description cannot be blank! Key description remains unchanged.")
      description = None

  #checks if user input valid unique ID
  if new_id:
    found_id = database.get_id(new_id)
    if found_id:
      errors.append(f"ID `{found_id['id']}` already exists from author {found_id['author']}. Please use a different ID. Key ID will remain `{id}`")
      new_id = None
    elif new_id and new_id.isdigit():
      errors.append(f"Key ID cannot be only numbers. Please choose an ID that is easily identifiable. Key ID will remain `{id}`")
      new_id = None

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

  #dict from key object
  new_dict = found_key.copy()

  all_values = [new_id,displayname,description,note,alt_note,subkeys,deconstruct,combine,inventory,journal,unique,repeating,stackable]
  #bool is true if every value in the given dict is None
  empty_dict = all(value is None for value in all_values)
  if empty_dict:
    embed_text = "The changes you submitted were invalid. Review the errors below. If you need help, try `/help editkey`. If something is wrong, contact Ironically-Tall."
  else:
    embed_text = "Review the changes and select a button below. Key data not mentioned is not being changed."
    if errors:
      embed_text = embed_text + "\nSome of your changes were invalid. Review the error section below, those changes have been discarded."
    if warnings:
      embed_text = embed_text + "\nSome of your inputs were valid but had issues. Those changes will still be updated for the key despite potential issues. Review the warnings before clicking a button."

  embed = discord.Embed(title=f"Editing key: {found_key['displayname']}\nID: **{id}**", description=embed_text)
  if new_id:
    new_dict["new_id"] = new_id
    embed.add_field(name="ID CHANGE", value=f"**Old:**: {found_key['id']}\n**New:** {new_id}\nThis will change the ID of this key, updating across all rooms and subkeys where it appears.", inline=False)
  if description:
    new_dict["description"] = description
    embed.add_field(name="Description", value=f"**Old:** {found_key['description']}\n**New:** {description}", inline=False)
  if displayname:
    new_dict["displayname"] = displayname
    new_dict["new_displayname"] = displayname
    embed.add_field(name="Displayname", value=f"**Old:** {found_key['displayname']}\n**New:** {displayname}", inline=False)
  if note:
    new_dict["note"] = note
    embed.add_field(name="Note", value=f"**Old:** {found_key['note']}\n**New:** {note}", inline=False)
  if alt_note:
    new_dict["alt_note"] = alt_note
    embed.add_field(name="Alt_Note", value=f"**Old:** {found_key['alt_note']}\n**New:** {alt_note}", inline=False)
  if subkeys:
    old_subkeys = ""
    for key in found_key["subkeys"]:
      old_subkeys += f"{key} x{found_key['subkeys'][key]}\n"
    new_dict["subkeys"] = new_subkeys
    embed.add_field(name="Subkeys", value=f"**Old:**\n{old_subkeys}\n**New:**\n{subkeys_string}", inline=False)
  if deconstruct is not None and deconstruct != new_dict["deconstruct"]:
    new_dict["deconstruct"] = deconstruct
    embed.add_field(name="Deconstruct", value=f"**Old:** {found_key['deconstruct']}\n**New:** {deconstruct}", inline=False)
  if combine is not None and combine != new_dict["combine"]:
    new_dict["combine"] = combine
    embed.add_field(name="Combine", value=f"**Old:** {found_key['combine']}\n**New:** {combine}", inline=False)
  if inventory is not None and inventory != new_dict["inventory"]:
    new_dict["inventory"] = inventory
    embed.add_field(name="Inventory", value=f"**Old:** {found_key['inventory']}\n**New:** {inventory}", inline=False)
  if journal is not None and journal != new_dict["journal"]:
    new_dict["journal"] = journal
    embed.add_field(name="Journal", value=f"**Old:** {found_key['journal']}\n**New:** {journal}", inline=False)
  if unique is not None and unique != new_dict["unique"]:
    new_dict["unique"] = unique
    embed.add_field(name="Unique", value=f"**Old:** {found_key['unique']}\n**New:** {unique}", inline=False)
  if repeating is not None and repeating != new_dict["repeating"]:
    new_dict["repeating"] = repeating
    embed.add_field(name="Repeating", value=f"**Old:** {found_key['repeating']}\n**New:** {repeating}", inline=False)
  if stackable is not None and stackable != new_dict["stackable"]:
    new_dict["stackable"] = stackable
    embed.add_field(name="Stackable", value=f"**Old:**{found_key['stackable']}\n**New:** {stackable}", inline=False)
  if warnings:
    embed.add_field(name=warn_title, value=warnings, inline=False)
  if errors:
    embed.add_field(name=error_title, value=f"- {errors}\nIf you need help, try `/help editkey`\ntip: you can press the 'up' key on a desktop keyboard to quickly re-enter the data", inline=False)
  if not embed.fields:
    embed.description = "ERROR"
    embed.add_field(name="No changes", value="No changes were made. You need to select one of the options to edit the key. If you're unsure, try /help editkey")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  view = discord.ui.View()
  if not empty_dict:
    edit_button = database.ConfirmButton(label="Make Changes", confirm=True, action="edit_key", id=id, dict=new_dict)
    cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
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