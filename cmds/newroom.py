import re

import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_interactions as permissions
from room import Room


#edits a room with whatever the user selects
@commands.hybrid_command(name="newroom", description="Create a new room. Leave options blank to keep the default value")
@app_commands.describe(
adventure="The adventure this new room will belong to. Case agnostic.",
id="Optionally input your own unique ID, must be unique across ALL player IDs!",
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
keys= "Keys that will be given when they enter the room, separate by commas.",
destroy= "Keys that will be removed from the player if they enter this room. Separate by commas",
lock= "Room becomes locked if player possesses these keys. Can use math expression",  
unlock= "Room will unlock if locked, if player possesses these keys. Can use math expression",  
hide= "Room will become hidden if player posesses these keys. Can use math expression",  
reveal= "Room will be revealed if hidden, if player posesses these keys. Can use math expression")
async def newroom(ctx,
    #giant block of arguments!
    adventure,
    id : str | None = None,
    displayname : str= "Room Name",
    description : str="You have wandered into a dark place. It is pitch black. You are likely to be eaten by a grue.",
    entrance : str="Go into the new room",
    alt_entrance : str="This path is blocked",
    exits : str | None = None,
    url : str | None = None,
    hidden : bool=False,
    locked : bool=False,
    once : bool=False,
    end : bool=False,
    deathnote : str | None = None,
    keys : str | None = None,
    destroy : str | None = None,
    lock : str | None = None,
    unlock : str | None = None,
    hide: str | None = None,
    reveal : str | None = None
                  ):
  #checks if player exists in the database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer before trying to make a new room.", ephemeral=True)
    return

  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    await ctx.reply("This command can only be used approved bot channels!", ephemeral=True)
    return

  #adds the adventure name to the room
  if not adventure:
    await ctx.reply("ERROR: You must specify an adventure for this room.", ephemeral=True)
    return
  else:
    found_adventure = database.get_adventure(adventure.lower())
    if not found_adventure:
      await ctx.reply(f"ERROR: The adventure {adventure} does not exist.", ephemeral=True)
      return
    else:
      adventure_of_room = found_adventure["name"].title()

  #for any potential issues with the room generation
  warnings = []

  #for errors in lock, unlock, reveal, hide conditions
  condition_errors = []

  #checks if user input valid unique ID
  if id:
    found_id = database.get_id(id)
    if found_id:
      await ctx.reply(f"ERROR: ID already exists. Please use a different ID.\n**ID:** {found_id['id']}\n**Author:** {found_id['author']}", ephemeral=True)
      return
    elif id.isdigit():
      await ctx.reply(f"ERROR: ID cannot be only numbers. Please choose and ID that is easily identifiable.", ephemeral=True)
      return

  #if no ID, generates a random one
  new_id = id if id else database.generate_unique_id()

  #turns string of exits to list of IDs
  new_exits = []
  if exits:
    new_exits = exits.replace(' ', '').split(',')
    for exit in new_exits:
      if not database.get_room(exit):
        warnings.append(f"Room {exit} does not exist. Hopefully you plan on creating it!")

  #parse keys into one dict
  keys_string = ""
  new_keys = {}
  if keys:
    pairs = keys.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_keys[item.strip()] = int(quantity)
        if not database.get_key(item.strip()):
          warnings.append(f"Key `{item.strip()}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
      except ValueError:
        await ctx.reply("Invalid key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the keys to one of somekey and three of otherkey)", ephemeral=True)
        return
    for key in new_keys:
      keys_string += f"{key} x{new_keys[key]}\n"

  #parse destroys into one dict
  destroy_string = ""
  new_destroy = {}
  if destroy:
    pairs = destroy.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_destroy[item.strip()] = int(quantity)
        if not database.get_key(item.strip()):
          warnings.append(f"Key `{item.strip()}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
      except ValueError:
        await ctx.reply("Invalid key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the keys to one of somekey and three of otherkey)", ephemeral=True)
        return
    for key in new_destroy:
      destroy_string += f"{key} x{new_destroy[key]}\n"

  #regex pattern for parsing conditionals:
  pattern = re.compile(r'^\s*([\w]+(?:\s*[+\-*/]\s*[\w]+)*)\s*([<>!=]=?)\s*([\w]+(?:\s*[+\-*/]\s*[\w]+)*)\s*$')

  #parse lock conditionals to string, checks for correct conditionals
  new_lock_string = []
  new_lock = []
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
        new_lock.append(condition)
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse unlock conditionals to string, checks for correct conditionals
  new_unlock_string = []
  new_unlock = []
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
        new_unlock.append(condition)
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse hide conditionals to string, checks for correct conditionals
  new_hide_string = []
  new_hide = []
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
        new_hide.append(condition)
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse reveal conditionals to string, checks for correct conditionals
  new_reveal_string = []
  new_reveal = []
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
        new_reveal.append(condition)
      left_expression = match.group(1)
      right_expression = match.group(3)
      keys_in_expression = re.findall(r'\b\w+\b', left_expression) + re.findall(r'\b\w+\b', right_expression)
      for key in keys_in_expression:
        if key.isdigit():
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #halts with error message if input in conditionals does not parse
  if condition_errors:
    error_message = "\n".join(condition_errors)
    await ctx.reply(f"There was an error with one or more of your conditional statements:\n{error_message}\n\nIf you need help, try `/architecthelp operators`", ephemeral=True)
    return

  #turns list of warnings to a string
  if warnings:
    warnings = "\n".join(warnings)

  #creates room object
  try:
    print("Room being created...")
    new_room = Room(
    id=new_id, 
    description=description,
    displayname=displayname, entrance=entrance, 
    alt_entrance=alt_entrance if alt_entrance else "", 
    exits= new_exits, 
    deathnote=deathnote if deathnote else "", 
    url=url if url else "", 
    hidden=hidden, locked=locked, end=end, once=once, 
    keys=new_keys if keys else None,
    destroy=new_destroy if destroy else None, 
    lock=new_lock if lock else None, 
    unlock=new_unlock if unlock else None, 
    hide=new_hide if hide else None, 
    reveal=new_reveal if reveal else None, 
    author=ctx.author.id, 
    adventure=adventure_of_room)
  except Exception as e:
    await ctx.reply(f"Error: There was a problem generating your room. Did you enter the data incorrectly? Ask Ironically-Tall for help if you're unsure.\nError:\n{e}", ephemeral=True)
    return
  dict = new_room.__dict__
  database.pp(dict)
  embed = discord.Embed(title=f"New room: {dict['displayname']}\nID: **{new_id}**\nAny room attributes not specified have been left at their default values.", description="Review the new room and select a button below:")
  embed.add_field(name="Displayname", value=f"{displayname}", inline=False)
  if description:
    embed.add_field(name="Description", value=f"{description}", inline=False)
  if entrance:
    embed.add_field(name="Entrance", value=f"{entrance}", inline=False)
  if alt_entrance:
    embed.add_field(name="Alt Entrance", value=f"{alt_entrance}", inline=False)
  if exits:
    embed.add_field(name="Exits", value=f"{exits.replace(' ', '').split(',')}", inline=False)
  if deathnote:
    embed.add_field(name="Deathnote", value=f"{deathnote}", inline=False)
  if url:
    embed.add_field(name="URL", value=f"{url}", inline=False)
  if keys:
    embed.add_field(name="Keys", value=keys_string, inline=False)
  if destroy:
    embed.add_field(name="Destroy", value=destroy_string, inline=False)
  if hidden:
    embed.add_field(name="Hidden", value=f"{hidden}", inline=False)
  if locked:
    embed.add_field(name="Locked", value=f"{locked}", inline=False)
  if end:
    embed.add_field(name="End", value=f"{end}", inline=False)
  if once:
    embed.add_field(name="Once", value=f"{once}", inline=False)
  if lock:
    new_lock_string = "\n".join(new_lock_string)
    embed.add_field(name="Lock", value=f"{new_lock_string}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be locked and greyed out.)", inline=False)
  if unlock:
    new_unlock_list = "\n".join(new_unlock_string)
    embed.add_field(name="Unlock", value=f"{new_unlock_list}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be unlocked and clickable if it was previously locked.)", inline=False)
  if hide:
    new_hide_list = "\n".join(new_hide_string)
    embed.add_field(name="Hide", value=f"{new_hide_list}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be hidden if not already.)", inline=False)
  if reveal:
    new_reveal_list = "\n".join(new_reveal_string)
    embed.add_field(name="Reveal", value=f"{new_reveal_list}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be revealed if it was hidden.)", inline=False)
  if warnings:
    embed.add_field(name="**WARNING:**", value=warnings)
  embed.set_footer(text=f"This room will be added to {adventure_of_room}.")
  edit_button = database.ConfirmButton(label="Create Room", confirm=True, action="new_room", dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel")
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

#returns adventures either owned or coauthored with matching name
@newroom.autocomplete('adventure')
async def autocomplete_newroom(interaction: discord.Interaction, current: str):
  if permissions.is_assistant_or_maintainer(interaction):
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
  bot.add_command(newroom)