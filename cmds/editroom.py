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
reveal= "Room will be revealed if hidden, if player posesses these keys. Can use math expression",
epilogue= "Whether the player is allowed to explore this adventure once it's completed"
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
    epilogue : bool | None = None
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

  #checks if user input valid unique ID
  if new_id:
    found_id = database.get_id(new_id)
    if found_id:
      await ctx.reply(f"ERROR: ID already exists. Please use a different ID.\n**ID:** {found_id['id']}\nID **Author:** {found_id['author']}", ephemeral=True)
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

  #parse lock into dict
  new_lock = {}
  new_lock_list = []
  new_lock_string = ""
  if lock:
    try:
      pairs = lock.split(',')
      for pair in pairs:
        item, quantity = pair.strip().split()
        new_lock[item.strip()] = int(quantity)
        new_lock_list.append(f"{item} x{quantity}")
        if not database.get_key(item.strip()):
          warnings.append(f"Key '{item.strip()}' does not exist. Did you enter the ID wrong or are you planning to create one later?")
    except ValueError:
      await ctx.reply("Invalid lock key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the keys to one of somekey and three of otherkey)", ephemeral=True)
      return
  new_lock_string = "\n".join(new_lock_list)
  #parse old lock to string
  old_lock = []
  old_lock_string = ""
  if found_room['lock']:
    for key, value in found_room['lock'].items():
      old_lock.append(f"{key} x{value}")
      old_lock_string = "\n".join(old_lock)
  else:
    old_lock_string = "None"

  #parse unlock into dict
  new_unlock = {}
  new_unlock_list = []
  new_unlock_string = ""
  if unlock:
    try:
      pairs = unlock.split(',')
      for pair in pairs:
        item, quantity = pair.strip().split()
        new_unlock[item.strip()] = int(quantity)
        new_unlock_list.append(f"{item} x{quantity}")
        if not database.get_key(item.strip()):
          warnings.append(f"Key '{item.strip()}' does not exist. Did you enter the ID wrong or are you planning to create one later?")
    except ValueError:
      await ctx.reply("Invalid unlock key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the unlocked keys to one of somekey and three of otherkey)", ephemeral=True)
      return
  new_unlock_string = "\n".join(new_unlock_list)
  #parse old unlock to string
  old_unlock = []
  old_unlock_string = ""
  if found_room['unlock']:
    for key, value in found_room['unlock'].items():
      old_unlock.append(f"{key} x{value}")
      old_unlock_string = "\n".join(old_unlock)
  else:
    old_unlock_string = "None"

  #parse hide into dict
  new_hide = {}
  new_hide_list = []
  new_hide_string = ""
  if hide:
    try:
      pairs = hide.split(',')
      for pair in pairs:
        item, quantity = pair.strip().split()
        new_hide[item.strip()] = int(quantity)
        new_hide_list.append(f"{item} x{quantity}")
        if not database.get_key(item.strip()):
          warnings.append(f"Key '{item.strip()}' does not exist. Did you enter the ID wrong or are you planning to create one later?")
    except ValueError:
      await ctx.reply("Invalid hide key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the hidden keys to one of somekey and three of otherkey)", ephemeral=True)
      return
  new_hide_string = "\n".join(new_hide_list)
  #parse old hide to string
  old_hide = []
  old_hide_string = ""
  if found_room['hide']:
    for key, value in found_room['hide'].items():
      old_hide.append(f"{key} x{value}")
      old_hide_string = "\n".join(old_hide)
  else:
    old_hide_string = "None"

  #parse reveal into dict
  new_reveal = {}
  new_reveal_list = []
  new_reveal_string = ""
  if reveal:
    try:
      pairs = reveal.split(',')
      for pair in pairs:
        item, quantity = pair.strip().split()
        new_reveal[item.strip()] = int(quantity)
        new_reveal_list.append(f"{item} x{quantity}")
        if not database.get_key(item.strip()):
          warnings.append(f"Key '{item.strip()}' does not exist. Did you enter the ID wrong or are you planning to create one later?")
    except ValueError:
      await ctx.reply("Invalid reveal key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the revealed keys to one of somekey and three of otherkey)", ephemeral=True)
      return
  new_reveal_string = "\n".join(new_reveal_list)
  #parse old reveal to string
  old_reveal = []
  old_reveal_string = ""
  if found_room['reveal']:
    for key, value in found_room['reveal'].items():
      old_reveal.append(f"{key} x{value}")
      old_reveal_string = "\n".join(old_reveal)
  else:
    old_reveal_string = "None"


  #copies the dict to alter without changing the completed dict
  new_dict = found_room.copy()

  #creates the embed to be displayed to the architect
  #only shows fields which have been altered
  embed = discord.Embed(title=f"Editing room:\n{found_room['displayname']}\nID: **{id}**", description="Review the changes and select a button below:")
  if new_id:
    new_dict["new_id"] = new_id
    embed.add_field(name="New ID", value=f"Old:\n{found_room['id']}\n\nNew:\n{new_id}\nChanging the ID of this room will update the ID across all rooms it is connected to", inline=True)
  if description:
    new_dict["description"] = description
    embed.add_field(name="Description", value=f"Old:\n{found_room['description']}\n\nNew:\n{description}", inline=False)
  if displayname:
    new_dict["new_displayname"] = displayname
    new_dict["displayname"] = displayname
    embed.add_field(name="Displayname", value=f"Old:\n{found_room['displayname']}\n\nNew:\n{displayname}", inline=False)
  if entrance:
    new_dict["entrance"] = entrance
    embed.add_field(name="Entrance", value=f"Old:\n{found_room['entrance']}\n\nNew:\n{entrance}", inline=False)
  if alt_entrance:
    new_dict["alt_entrance"] = alt_entrance
    embed.add_field(name="Alt Entrance", value=f"Old:\n{found_room['alt_entrance']}\n\nNew:\n{alt_entrance}", inline=False)
  if new_exits:
    new_dict["exits"] = new_exits
    embed.add_field(name="Exits", value=f"Old:\n{found_room['exits']}\n\nNew:\n{new_exits}", inline=False)
  if deathnote:
    new_dict["deathnote"] = deathnote
    embed.add_field(name="Deathnote", value=f"Old:\n{found_room['deathnote']}\n\nNew:\n{deathnote}", inline=False)
  if url:
    new_dict["url"] = url
    embed.add_field(name="URL", value=f"Old:\n{found_room['url']}\n\nNew:\n{url}", inline=False)
  if keys:
    new_dict["keys"] = new_keys
    embed.add_field(name="Keys", value=f"Old:\n{old_keys_string}\n\nNew:\n{new_keys_string}", inline=False)
  if hidden:
    new_dict["hidden"] = hidden
    embed.add_field(name="Hidden", value=f"Old:\n{found_room['hidden']}\n\nNew:\n{hidden}", inline=False)
  if locked:
    new_dict["locked"] = locked
    embed.add_field(name="Locked", value=f"Old:\n{found_room['locked']}\n\nNew:\n{locked}", inline=False)
  if end:
    new_dict["end"] = end
    embed.add_field(name="End", value=f"Old:\n{found_room['end']}\n\nNew:\n{end}", inline=False)
  if once:
    new_dict["once"] = once
    embed.add_field(name="Once", value=f"Old: {found_room['once']}\n\nNew:\n{once}", inline=False)
  if lock:
    new_dict["lock"] = new_lock
    embed.add_field(name="Lock", value=f"Old: {old_lock_string}\n\nNew:\n{new_lock_string}", inline=False)
  if unlock:
    new_dict["unlock"] = new_unlock
    embed.add_field(name="Unlock", value=f"Old:\n{old_unlock_string}\n\nNew:\n{new_unlock_string}", inline=False)
  if hide:
    new_dict["hide"] = new_hide
    embed.add_field(name="Hide", value=f"Old:\n{old_hide_string}\n\nNew:\n{new_hide_string}", inline=False)
  if reveal:
    new_dict["reveal"] = new_reveal
    embed.add_field(name="Reveal", value=f"Old:\n{old_reveal_string}\n\nNew:\n{new_reveal_string}", inline=False)
  if destroy:
    new_dict["destroy"] = new_destroy
    embed.add_field(name="Destroy", value=f"Old:\n{old_destroy_string}\n\nNew:\n{new_destroy_string}", inline=False)
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