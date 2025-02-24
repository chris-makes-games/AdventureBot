import re

import discord
from discord import app_commands
from discord.ext import commands

import truncate
import database
import perms_interactions as permissions
from room import Room


#creates a room with whatever the user selects
#default values sent if no selections are made
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
    id : str | str = "",
    displayname : str= "Default Room Name",
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
    adventure_of_room = found_adventure["name"].title()

  #for issues which can still safely be sent to room
  warnings = []

  #for errors in any attribute that cannot be sent to room
  errors = []
  
  #check for None assignment attempts in mandatory fields
  if id:
    id, warning = truncate.id(id)
    if warning:
      warnings.append(warning)
    if id.lower() == "none" or id.strip() == "":
      id = database.generate_unique_id()
      errors.append(f"You cannot have a blank room ID! Room must have an ID. Random ID generated instead: `{id}`")
  if entrance:
    if entrance.lower() == "none" or entrance.strip() == "":
      errors.append(f"Room entrance cannot be blank! Room entrance set to generic default.")
      entrance = "Go into the new room"
  if alt_entrance:
    if alt_entrance.lower() == "none" or alt_entrance.strip() == "":
      errors.append(f"Alt entrance cannot be blank, all rooms must have one! Room alt entrance set to generic default.")
      alt_entrance = "This path is blocked"
  if description:
    if description.lower() == "none" or description.strip() == "":
      errors.append(f"Description cannot be blank! Room description set to default generic.")
      description = "You have wandered into a dark place. It is pitch black. You are likely to be eaten by a grue."
  if displayname:
    if displayname.lower() == "none" or displayname.strip() == "":
      errors.append(f"Display name cannot be blank! Room display name set to default generic.")
      displayname = "Default Room Name"

  #checks if user input valid unique ID
  if id:
    new_id = id
    found_id = database.get_id(new_id)
    if found_id:
      new_id = database.generate_unique_id()
      warnings.append(f"ID `{found_id['id']}` already exists from author {found_id['author']}. A random ID was generated instead: `{new_id}`")
    elif id == "none" or id == "None":
      new_id = database.generate_unique_id()
      warnings.append(f"Room must have an ID. Random ID generated: `{new_id}`")
    elif id and id.isdigit():
      new_id = database.generate_unique_id()
      warnings.append(f"Room ID cannot be only numbers. Random ID generated instead: `{new_id}`")
  else:
    #if no ID, generates a random one
    new_id = database.generate_unique_id()
    warnings.append(f"Random ID generated for room: `{new_id}`")

  if description:
    if len(description) > 6000:
      errors.append("The description of your room cannot exceed 6000 characters! That's only around 1,200 words.")
    elif len(description) > 1024:
      description_string = description[:1000]
      description_string += "(...)"

  #parses exits into usable list and validates the ID
  #ensures a room can have only four exits
  new_exits = []
  new_exits_string = []
  if exits:
    new_exits = exits.replace(' ', '').split(',')
    if len(new_exits) > 4:
      new_exits = new_exits[:4]
      warnings.append("You can only have a maximum of four exits in a room! Only the first four exits were saved.")
    for exit in new_exits:
      if exit == "":
        continue
      new_exits_string.append("`" + exit + "`")
      if not database.get_room(exit):
        warnings.append(f"Room '{exit}' does not exist. Hopefully you plan on creating it! Until you do, this exit will not appear!")
    new_exits_string = "- " + "\n- ".join(new_exits_string)
  
  #parse keys into one dict
  keys_string = ""
  new_keys = {}
  if keys:
    pairs = keys.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_keys[item.strip()] = int(quantity)
      except ValueError:
        errors.append(f"Invalid key format: `{pair}`\n(must be in the format `key_id <number>`)")
        continue
      if not database.get_key(item.strip()):
          warnings.append(f"Key `{item.strip()}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
  if new_keys:
    for key in new_keys:
      keys_string += f"`{key}` x{new_keys[key]}\n"
  else:
    keys = None

  #parse destroys into one dict
  destroy_string = ""
  new_destroy = {}
  if destroy:
    pairs = destroy.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_destroy[item.strip()] = int(quantity)
      except ValueError:
        errors.append(f"Invalid destroy key format: `{pair}`\n(must be in the format `key_id <number>`)")
        continue
      if not database.get_key(item.strip()):
          warnings.append(f"Key `{item.strip()}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
  if new_destroy:
    for key in new_destroy:
      destroy_string += f"`{key}` x{new_destroy[key]}\n"
  else:
    destroy = None

  #parse lock conditionals to string, checks for correct conditionals
  new_lock_string = []
  new_lock = []
  if lock:
    conditions = lock.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      if not database.safe_parse(new_condition):
        errors.append(f"invalid lock expression syntax: `{new_condition.replace('==', '=')}`")
        continue
      new_lock.append(new_condition)
      new_string = "`" + new_condition.replace('==', '=') + "`"
      new_lock_string.append(new_string)
      keys_in_expression = re.findall(r'\b\w+\b', new_condition)
      for key in keys_in_expression:
        #skips words if they aren't supposed to be keys
        if key.isdigit() or key.lower() == "and" or key.lower() == "or":
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
    if not new_lock_string:
      lock = None

  #parse unlock conditionals to string, checks for correct conditionals
  new_unlock_string = []
  new_unlock = []
  if unlock:
    conditions = unlock.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      if not database.safe_parse(new_condition):
        errors.append(f"invalid unlock expression syntax: `{new_condition.replace('==', '=')}`")
        continue
      new_unlock.append(new_condition)
      new_string = "`" + new_condition.replace('==', '=') + "`"
      new_unlock_string.append(new_string)
      keys_in_expression = re.findall(r'\b\w+\b', new_condition)
      for key in keys_in_expression:
        #skips words if they aren't supposed to be keys
        if key.isdigit() or key.lower() == "and" or key.lower() == "or":
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
    if not new_unlock_string:
      unlock = None

  #parse hide conditionals to string, checks for correct conditionals
  new_hide_string = []
  new_hide = []
  if hide:
    conditions = hide.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      if not database.safe_parse(new_condition):
        errors.append(f"invalid hide expression syntax: `{new_condition.replace('==', '=')}`")
        continue
      new_hide.append(new_condition)
      new_string = "`" + new_condition.replace('==', '=') + "`"
      new_hide_string.append(new_string)
      keys_in_expression = re.findall(r'\b\w+\b', new_condition)
      for key in keys_in_expression:
        #skips words if they aren't supposed to be keys
        if key.isdigit() or key.lower() == "and" or key.lower() == "or":
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
    if not new_hide_string:
      hide = None

  #parse reveal conditionals to string, checks for correct conditionals
  new_reveal_string = []
  new_reveal = []
  if reveal:
    conditions = reveal.split(',')
    for condition in conditions:
      new_condition = condition.strip()
      new_condition = re.sub(r'\s*([<>!=]=?|[+\-*/])\s*', r' \1 ', new_condition)
      new_condition = re.sub(r'(?<![!<>])=(?!=)', '==', new_condition)
      if not database.safe_parse(new_condition):
        errors.append(f"reveal condition: `{new_condition.replace('==', '=')}`")
        continue
      new_reveal.append(new_condition)
      new_string = "`" + new_condition.replace('==', '=') + "`"
      new_reveal_string.append(new_string)
      keys_in_expression = re.findall(r'\b\w+\b', new_condition)
      for key in keys_in_expression:
        #skips words if they aren't supposed to be keys
        if key.isdigit() or key.lower() == "and" or key.lower() == "or":
          continue
        if not database.get_key(key):
          warnings.append(f"Key `{key}` does not exist. Did you enter the ID wrong or are you planning to create one later?")
    if not new_reveal_string:
      reveal = None

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
    print(e)
    return
  
  #dict from the created room to be sent to database
  dict = new_room.__dict__
  database.pp(dict)

  all_values = [new_id,description,displayname,entrance,alt_entrance,exits,url,hidden,locked,once,end,deathnote,keys,destroy,lock,unlock,hide,reveal]
  #bool is true if every value in the given dict is None
  empty_dict = all(all_values)
  if empty_dict:
    embed_text = "The room information you submitted was invalid. Review the errors below. If you need help, try `/help editroom`. If something is wrong, contact Ironically-Tall."
  else:
    embed_text = "Review the new room and select a button below"
  if errors:
    embed_text = embed_text + "\nSome of your inputs were invalid. Review the error section below, those invalid changes have been discarded."
  if warnings:
    embed_text = embed_text + "\nSome of your inputs were valid but had issues. Those changes will still be created in the room despite potential issues. Review the warnings before clicking a button."

  embed = discord.Embed(title=f"New room: {dict['displayname']}\nID: `{new_id}`\nAny room attributes not specified have been left at their default values.", description=embed_text)
  embed.add_field(name="Displayname", value=f"{displayname}", inline=False)
  if description:
    embed.add_field(name="Description", value=f"{description}", inline=False)
  if entrance:
    embed.add_field(name="Entrance", value=f"{entrance}", inline=False)
  if alt_entrance:
    embed.add_field(name="Alt Entrance", value=f"{alt_entrance}", inline=False)
  if exits:
    embed.add_field(name="Exits", value=f"{new_exits_string}", inline=False)
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
    new_lock_string = "\n- ".join(new_lock_string)
    embed.add_field(name="Lock", value=f"- {new_lock_string}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be locked and greyed out.)", inline=False)
  if unlock:
    new_unlock_string = "\n- ".join(new_unlock_string)
    embed.add_field(name="Unlock", value=f"- {new_unlock_string}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be unlocked and clickable if it was previously locked.)", inline=False)
  if hide:
    new_hide_string = "\n- ".join(new_hide_string)
    embed.add_field(name="Hide", value=f"- {new_hide_string}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be hidden if not already.)", inline=False)
  if reveal:
    new_reveal_string = "\n- ".join(new_reveal_string)
    embed.add_field(name="Reveal", value=f"- {new_reveal_string}\n(If all of these are true when the player is in an adjescant room, then the button for this room will be revealed if it was hidden.)", inline=False)
  if warnings:
    embed.add_field(name=warn_title, value=f"- {warnings}", inline=False)
  if errors:
    embed.add_field(name=error_title, value=f"- {errors}\nIf you need help, try `/help newroom`\ntip: you can press the 'up' key on a desktop keyboard to quickly re-enter the data", inline=False)
  embed.set_footer(text=f"This room will be added to {adventure_of_room}.")
  view = discord.ui.View()
  if not empty_dict:
    edit_button = database.ConfirmButton(label="Create Room", confirm=True, action="new_room", dict=dict)
    cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel")
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