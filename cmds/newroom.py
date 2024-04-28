import discord
from discord import app_commands
from discord.ext import commands

import database
from room import Room


#edits a room with whatever the user selects
@commands.hybrid_command(name="newroom", description="Create a new room. Leave options blank to keep the default value")
@app_commands.describe(
id= "Optionally input your own unique ID, must be unique across ALL player IDs!",
displayname="The title of the room displayed to players",
description="Main description of the room displayed to players. Usually second person.",
entrance="Description of a choice that leads to this room",
alt_entrance="Description of the choice when the room is blocked and cannot be selected",
exits= "IDs of rooms that can be selected from this room, separated by commas",
deathnote="For endings that kill the player, describe how they died. No pronouns",
url= "URL to an image to display in the room next to the description",
hidden= "This room will not appear as a choice unless the player has the keys in 'reveal'",
locked= "The choice for this room will be alt_text and be unselectable unless player has keys in 'unlock'",
end= "Room that ends the adventure. Include a deathnote if the ending is a death",
once= "If the player selects the option to go into this room, the option to do so will not appear again",
keys= "Keys that will be given when they enter the room, separate by commas. <keyid> 1, <keyid> 4",    
lock= "Room becomes locked. Example: key1 > 4 and key2 = 0",  
unlock= "Room will unlock if locked",  
hide= "Room will become hidden",  
reveal= "Room will be revealed if hidden",  
destroy= "Keys that will be removed from the player if they enter this room. Separate by commas")
async def newroom(ctx,
    #giant block of arguments!
    id : str | None = None,
    displayname : str= "Room Name",
    description : str="You have wandered into a dark place. It is pitch black. You are likely to be eaten by a grue.",
    entrance : str="Go into the new room",
    alt_entrance : str | None = None,
    exits : str | None = None,
    deathnote : str | None = None,
    url : str | None = None,
    hidden : bool=False,
    locked : bool=False,
    end : bool=False,
    once : bool=False,
    keys : str | None = None,
    lock : str | None = None,
    unlock : str | None = None,
    hide: str | None = None,
    reveal : str | None = None,
    destroy : str | None = None,
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

  #turns string of exits to list of IDs
  new_exits = []
  if exits:
    new_exits = exits.replace(' ', '').split(',')
    for exit in new_exits:
      if not database.get_room(exit):
        warnings.append(f"Room {exit} does not exist. Hopefully you plan on creating it!")

  #parse keys into one dict
  new_keys = {}
  if keys:
    pairs = keys.split(',')
    for pair in pairs:
      item, quantity = pair.strip().split()
      new_keys[item.strip()] = int(quantity)
      if not database.get_key(item.strip()):
        warnings.append(f"Key {item.strip()} does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #parse destroys into one dict
  new_destroy = {}
  if destroy:
    pairs = destroy.split(',')
    for pair in pairs:
      item, quantity = pair.strip().split()
      new_destroy[item.strip()] = int(quantity)
      if not database.get_key(item.strip()):
        warnings.append(f"Key {item.strip()} does not exist. Did you enter the ID wrong or are you planning to create one later?")

  #turns list of warnings to a string
  if warnings:
    warnings = "\n".join(warnings)

  #adds the adventure name to the room
  if player["edit_thread"]:
    adventure_of_room = player["edit_thread"][1]
  else:
    adventure_of_room = "Error: Unknown Adventure"

  #creates room object
  try:
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
    lock=lock if lock else "", 
    unlock=unlock if unlock else "", 
    hide=hide if hide else "", 
    reveal=reveal if reveal else "", 
    destroy=new_destroy if destroy else None, 
    author=ctx.author.id, 
    adventure=adventure_of_room)
  except Exception as e:
    await ctx.reply(f"Error: There was a problem generating your room. Did you enter the data incorrectly? Ask Ironically-Tall for help if you're unsure.Error:\n{e}", ephemeral=True)
    return
  dict = new_room.__dict__
  embed = discord.Embed(title=f"New room: {dict['displayname']}\nID: **{new_id}** (automatically generated)\nAny room attributes not specified have been left at their default values.", description="Review the new room and select a button below:")
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
    embed.add_field(name="Keys", value=f"{keys.replace(' ', '').split(',')}", inline=False)
  if hidden:
    embed.add_field(name="Hidden", value=f"{hidden}", inline=False)
  if locked:
    embed.add_field(name="Locked", value=f"{locked}", inline=False)
  if end:
    embed.add_field(name="End", value=f"{end}", inline=False)
  if once:
    embed.add_field(name="Once", value=f"{once}", inline=False)
  if lock:
    embed.add_field(name="Lock", value=f"{lock.replace(' ', '').split(',')}", inline=False)
  if unlock:
    embed.add_field(name="Unlock", value=f"{unlock.replace(' ', '').split(',')}", inline=False)
  if hide:
    embed.add_field(name="Hide", value=f"{hide.replace(' ', '').split(',')}", inline=False)
  if reveal:
    embed.add_field(name="Reveal", value=f"{reveal.replace(' ', '').split(',')}", inline=False)
  if destroy:
    embed.add_field(name="Destroy", value=f"{destroy.replace(' ', '').split(',')}", inline=False)
  if warnings:
    embed.add_field(name="**WARNING:**", value=warnings)
  embed.set_footer(text=f"This room will be added to {adventure_of_room}.")
  edit_button = database.ConfirmButton(label="Create Room", confirm=True, action="new_room", dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel")
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(newroom)