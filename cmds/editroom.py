import re

import discord
from discord import app_commands
from discord.ext import commands

import database


#edits a room with whatever the user selects
@commands.hybrid_command(name="editroom", description="Edit room attributes. Leave options blank to keep the current value")
@app_commands.describe(
new_id = "Change room ID. Changing this will also update all mentions of this room",
displayname="The title of the room displayed to players",
description="Main description of the room displayed to players. Usually second person.",
entrance="Description of a choice that leads to this room",
alt_entrance="Description of the choice when the room is blocked and cannot be selected",
exits= "IDs of rooms that can be selected to travel to from this room, separated by commas",
url= "URL to an image to display in the room next to the description",
hidden= "This room will not appear as a choice unless the player has the keys in 'reveal'",
locked= "The choice for this room will be alt_text and be unselectable unless player has keys in 'unlock'",
once= "If the player selects the option to go into this room, the option to do so will not appear again",
end= "Room that ends the adventure. Include a deathnote if the ending is a death",
deathnote="For endings that kill the player, describe how they died. Ex; 'Killed by X during Y'",
keys= "Keys that will be given when they enter the room, separate by commas. <keyid> 1, <keyid> 4",
destroy= "Keys that will be removed from the player if they enter this room. Separate by commas",
lock= "Room becomes locked if player possesses these keys. Can use math expression",  
unlock= "Room will unlock if locked, if player possesses these keys. Can use math expression",  
hide= "Room will become hidden if player posesses these keys. Can use math expression",  
reveal= "Room will be revealed if hidden, if player posesses these keys. Can use math expression"
)

async def editroom(ctx, id: str,
    #giant block of optional arguments!
    new_id: str | None = None,
    description : str | None = None,
    displayname : str | None = None,
    entrance : str | None = None,
    alt_entrance : str | None = None,
    exits : str | None = None,
    url : str | None = None,
    hidden : bool | None = None,
    locked : bool | None = None,
    once : bool | None = None,
    end : bool | None = None,
    deathnote : str | None = None,
    keys : str | None = None,
    destroy : str | None = None,
    lock : str | None = None,
    unlock : str | None = None,
    hide: str | None = None,
    reveal : str | None = None,
                  ):

  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return

  #checks if command was issued in protected channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return
  
  #ensures the room ID entered is valid
  found_room = database.rooms.find_one({"id": id})
  if not found_room:
    await ctx.reply(f"Error: No room found with id `{id}`! Double check the ID, you should just select a room from the list. If you're sure it should be correct, contact Ironically-Tall", ephemeral=True)
    return

  #warnings for exits not found
  warnings = []

  #for errors in lock, unlock, reveal, hide conditions
  condition_errors = []

  #checks if user input valid unique ID
  if new_id:
    found_id = database.get_id(new_id)
    if found_id:
      await ctx.reply(f"ERROR: ID already exists. Please use a different ID.\n**ID:** {found_id['id']}\nID **Author:** {found_id['author']}", ephemeral=True)
      return
    elif new_id.isdigit():
      await ctx.reply(f"ERROR: ID cannot be only numbers. Please choose and ID that is easily identifiable.", ephemeral=True)
      return

  #parses exits into usable list and validates the ID
  new_exits = []
  if exits:
    new_exits = exits.replace(' ', '').split(',')
    for exit in new_exits:
      if not database.get_room(exit):
        warnings.append(f"Room '{exit}' does not exist. Hopefully you plan on creating it!")
  
  #parse keys into dict
  new_keys = {}
  new_keys_list = []
  new_keys_string = ""
  if keys:
    pairs = keys.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_keys[item.strip()] = int(quantity)
        new_keys_list.append(f"{item} x{quantity}")
        if not database.get_key(item.strip()):
          warnings.append(f"Key '{item.strip()}' does not exist. Did you enter the ID wrong or are you planning to create one later?")
      except ValueError:
        await ctx.reply("Invalid key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the keys to one of somekey and three of otherkey)", ephemeral=True)
        return
  new_keys_string = "\n".join(new_keys_list)
  #parse old keys to string
  old_keys = []
  old_keys_string = ""
  if found_room['keys']:
    for key, value in found_room['keys'].items():
      old_keys.append(f"{key} x{value}")
      old_keys_string = "\n".join(old_keys)
  else:
    old_keys_string = "None"

  #parse destroy into dict
  new_destroy = {}
  new_destroy_list = []
  new_destroy_string = ""
  if destroy:
    try:
      pairs = destroy.split(',')
      for pair in pairs:
        item, quantity = pair.strip().split()
        new_destroy[item.strip()] = int(quantity)
        new_destroy_list.append(f"{item} : {quantity}")
        if not database.get_key(item.strip()):
          warnings.append(f"Key '{item.strip()}' does not exist. Did you enter the ID wrong or are you planning to create one later?")
    except ValueError:
      await ctx.reply("Invalid destroy key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the destroyed keys to one of somekey and three of otherkey)", ephemeral=True)
      return
  new_destroy_string = "\n".join(new_destroy_list)
  #parse old destroy to string
  old_destroy = []
  old_destroy_string = ""
  if found_room['destroy']:
    for key, value in found_room['destroy'].items():
      old_keys.append(f"{key} x{value}")
      old_destroy_string = "\n".join(old_destroy)
  else:
    old_destroy_string = "None"

  #regex pattern for parsing conditionals:
  pattern = re.compile(r'^\s*([\w]+(?:\s*[+\-*/]\s*[\w]+)*)\s*([<>!=]=?)\s*([\w]+(?:\s*[+\-*/]\s*[\w]+)*)\s*$')

  #parse lock conditionals to string, checks for correct conditionals
  new_lock_string = []
  if lock:
    conditions = lock.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      match = pattern.match(new_condition)
      if not match:
        condition_errors.append(f"lock condition: `{new_condition.replace('==', '=')}`")
        continue
      else:
        new_lock_string.append("- " + new_condition.replace("==", "="))
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key {key} does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse unlock conditionals to string, checks for correct conditionals
  new_unlock_string = []
  if unlock:
    conditions = unlock.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      match = pattern.match(new_condition)
      if not match:
        condition_errors.append(f"unlock condition: `{new_condition.replace('==', '=')}`")
        continue
      else:
        new_unlock_string.append("- " + new_condition.replace("==", "="))
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key {key} does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse hide conditionals to string, checks for correct conditionals
  new_hide_string = []
  if hide:
    conditions = hide.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      match = pattern.match(new_condition)
      if not match:
        condition_errors.append(f"hide condition: `{new_condition.replace('==', '=')}`")
        continue
      else:
        new_hide_string.append("- " + new_condition.replace("==", "="))
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key {key} does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse reveal conditionals to string, checks for correct conditionals
  new_reveal_string = []
  if reveal:
    conditions = reveal.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      match = pattern.match(new_condition)
      if not match:
        condition_errors.append(f"reveal condition: `{new_condition.replace('==', '=')}`")
        continue
      else:
        new_reveal_string.append("- " + new_condition.replace("==", "="))
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key {key} does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #halts with error message if input in conditionals does not parse
  if condition_errors:
    error_message = "\n".join(condition_errors)
    await ctx.reply(f"There was an error with one or more of your conditional statements:\n{error_message}\n\nIf you need help, try `/architecthelp operators`", ephemeral=True)
    return

  #copies the dict to alter without changing the completed dict
  new_dict = found_room.copy()

  #creates the embed to be displayed to the architect
  #only shows fields which have been altered
  embed = discord.Embed(title=f"Editing room:\n{found_room['displayname']}\nID: **{id}**", description="Review the changes and select a button below:")
  if new_id:
    new_dict["new_id"] = new_id
    embed.add_field(name="New ID", value=f"\nOld:\n{found_room['id']}\n\nNew:\n{new_id}\nChanging the ID of this room will update the ID across all rooms it is connected to", inline=True)
  if description:
    new_dict["description"] = description
    embed.add_field(name="Description", value=f"\nOld:\n{found_room['description']}\n\nNew:\n{description}", inline=False)
  if displayname:
    new_dict["new_displayname"] = displayname
    new_dict["displayname"] = displayname
    embed.add_field(name="Displayname", value=f"\nOld:\n{found_room['displayname']}\n\nNew:\n{displayname}", inline=False)
  if entrance:
    new_dict["entrance"] = entrance
    embed.add_field(name="Entrance", value=f"\nOld:\n{found_room['entrance']}\n\nNew:\n{entrance}", inline=False)
  if alt_entrance:
    new_dict["alt_entrance"] = alt_entrance
    embed.add_field(name="Alt Entrance", value=f"\nOld:\n{found_room['alt_entrance']}\n\nNew:\n{alt_entrance}", inline=False)
  if new_exits:
    new_dict["exits"] = new_exits
    old_data = found_room["exits"] if found_room["exits"] else None
    embed.add_field(name="Exits", value=f"\nOld:\n{old_data}\n\nNew:\n{new_exits}", inline=False)
  if deathnote:
    new_dict["deathnote"] = deathnote
    old_data = found_room["deathnote"] if found_room["deathnote"] else "None"
    embed.add_field(name="Deathnote", value=f"\nOld:\n{old_data}\n\nNew:\n{deathnote}", inline=False)
  if url:
    new_dict["url"] = url
    old_data = found_room["url"] if found_room["url"] else "None"
    embed.add_field(name="URL", value=f"\nOld:\n{old_data}\n\nNew:\n{url}", inline=False)
  if keys:
    new_dict["keys"] = new_keys
    embed.add_field(name="Keys", value=f"\nOld:\n{old_keys_string}\n\nNew:\n{new_keys_string}", inline=False)
  if hidden is not None and hidden != new_dict["hidden"]:
    new_dict["hidden"] = hidden
    embed.add_field(name="Hidden", value=f"\nOld:\n{found_room['hidden']}\n\nNew:\n{hidden}", inline=False)
  if locked is not None and locked != new_dict["locked"]:
    new_dict["locked"] = locked
    embed.add_field(name="Locked", value=f"\nOld:\n{found_room['locked']}\n\nNew:\n{locked}", inline=False)
  if end is not None and end != new_dict["end"]:
    new_dict["end"] = end
    embed.add_field(name="End", value=f"\nOld:\n{found_room['end']}\n\nNew:\n{end}", inline=False)
  if once is not None and once != new_dict["once"]:
    new_dict["once"] = once
    embed.add_field(name="Once", value=f"\nOld:\n{found_room['once']}\n\nNew:\n{once}", inline=False)
  if lock:
    new_dict["lock"] = new_lock_string
    new_lock_string = "\n".join(new_lock_string)
    old_data = found_room["lock"] if found_room["lock"] else "None"
    embed.add_field(name="Lock", value=f"\nOld:\n{old_data}\n\nNew:\n{new_lock_string}", inline=False)
  if unlock:
    new_dict["unlock"] = new_unlock_string
    new_unlock_string = "\n".join(new_unlock_string)
    old_data = found_room["unlock"] if found_room["unlock"] else "None"
    embed.add_field(name="Unlock", value=f"\nOld:\n{old_data}\n\nNew:\n{new_unlock_string}", inline=False)
  if hide:
    new_dict["hide"] = new_hide_string
    new_hide_string = "\n".join(new_hide_string)
    old_data = found_room["hide"] if found_room["hide"] else "None"
    embed.add_field(name="Hide", value=f"\nOld:\n{old_data}\n\nNew:\n{new_hide_string}", inline=False)
  if reveal:
    new_dict["reveal"] = new_reveal_string
    new_reveal_string = "\n".join(new_reveal_string)
    old_data = found_room["reveal"] if found_room["reveal"] else "None"
    embed.add_field(name="Reveal", value=f"\nOld:\n{old_data}\n\nNew:\n{new_reveal_string}", inline=False)
  if destroy:
    new_dict["destroy"] = new_destroy
    embed.add_field(name="Destroy", value=f"\nOld:\n{old_destroy_string}\n\nNew:\n{new_destroy_string}", inline=False)
  #returns error if no embed fields were added
  if not embed.fields:
    embed.description = "ERROR"
    embed.add_field(name="No changes", value="No changes were made. You need to select one of the options to edit the room. If you're unsure, try /help editroom")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #adds warning to bottom of dict
  if warnings:
    embed.add_field(name="**WARNING**", value="\n".join(warnings), inline=False)
  edit_button = database.ConfirmButton(label="Make Changes", confirm=True, action="edit_room", id=id, dict=new_dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

#returns rooms with matching id OR matching displayname
@editroom.autocomplete('id')
async def autocomplete_editroom(interaction: discord.Interaction, current: str):
  room_query = database.rooms.find(
    {"author": interaction.user.id,
      "$or": [
{"id": {"$regex": re.escape(current), "$options": "i"}},
{"displayname": {"$regex": re.escape(current),"$options": "i"}}
         ]},
{"id": 1, "displayname": 1, "_id": 0}
    )
  room_info = [(room["id"], room["displayname"]) for room in room_query]
  choices = [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_info[:25]]
  return choices

async def setup(bot):
  bot.add_command(editroom)