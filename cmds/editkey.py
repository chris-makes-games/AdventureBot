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
unique="If they player adds this to their inventory, they may not do so again",
repeating="Every time the player enters the room, the room will try to give them the key",
stackable="Whether The player may have more than one.")
async def editkey(ctx, id : str,
  #giant block of arguments!
  new_id : str | None = None,
  displayname : str | None = None,
  description : str | None = None,
  note : str | None = None,
  alt_note : str | None=None,
  subkeys : str | None = None,
  deconstruct : bool | None = None,
  unique : bool | None = None,
  repeating : bool | None = None,
  stackable : bool | None = None,
                ):
  
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return

  #warnings for subkeys not found
  warnings = []

  #error for no key found
  found_key = database.keys.find_one({"id": id})
  if not found_key:
    await ctx.reply(f"Error: No key found with id **{id}**! Double check you've selected a valid key. If you need to make a new key, try /newkey", ephemeral=True)
    return

  #checks if user input valid unique ID
  if id and database.get_id(new_id):
    found_id = database.get_id(new_id)
    await ctx.reply(f"ERROR: ID already exists. Please use a different ID.\n**ID:** {new_id}\n**Author:** {found_id['author']}", ephemeral=True)
    return

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
        return
    for key in new_subkeys:
      subkeys_string += f"{key} x{new_subkeys[key]}\n"
  
  new_dict = found_key.copy()
  embed = discord.Embed(title=f"Editing key: {found_key['displayname']}\nID: **{id}**", description="Review the changes and select a button below:")
  if new_id:
    new_dict["new_id"] = new_id
    embed.add_field(name="ID CHANGE", value=f"**Old:**: {found_key['id']}\n**New:** {new_id}\nThis will change the ID of this key, updating across all rooms and subkeys where it appears.", inline=False)
  if description:
    new_dict["description"] = description
    embed.add_field(name="Description", value=f"**Old:** {found_key['description']}\n**New:** {description}", inline=False)
  if displayname:
    new_dict["displayname"] = displayname
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
  if unique:
    new_dict["unique"] = unique
    embed.add_field(name="Unique", value=f"**Old:** {found_key['unique']}\n**New:** {unique}", inline=False)
  if repeating:
    new_dict["repeating"] = repeating
    embed.add_field(name="Repeating", value=f"**Old:** {found_key['repeating']}\n**New:** {repeating}", inline=False)
  if deconstruct:
    new_dict["deconstruct"] = deconstruct
    embed.add_field(name="Deconstruct", value=f"**Old:** {found_key['deconstruct']}\n**New:** {deconstruct}", inline=False)
  if stackable:
    new_dict["stackable"] = stackable
    embed.add_field(name="Stackable", value=f"**Old:**{found_key['stackable']}\n**New:** {stackable}", inline=False)
  
  if not embed.fields:
    embed.description = "ERROR"
    embed.add_field(name="No changes", value="No changes were made. You need to select one of the options to edit the key. If you're unsure, try /help editkey")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  if warnings:
    embed.add_field(name="**WARNING**", value="\n".join(warnings), inline=False)
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