import re

import discord
from discord import app_commands
from discord.ext import commands

import database
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
    alt_entrance : str | None = None,
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
  keys_string = ""
  new_keys = {}
  if keys:
    pairs = keys.split(',')
    for pair in pairs:
      try:
        item, quantity = pair.strip().split()
        new_keys[item.strip()] = int(quantity)
        if not database.get_key(item.strip()):
          warnings.append(f"Key {item.strip()} does not exist. Did you enter the ID wrong or are you planning to create one later?")
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
          warnings.append(f"Key {item.strip()} does not exist. Did you enter the ID wrong or are you planning to create one later?")
      except ValueError:
        await ctx.reply("Invalid key format. Please use this format:\n`somekey 1, otherkey 3`\n(This will set the keys to one of somekey and three of otherkey)", ephemeral=True)
        return
    for key in new_destroy:
      destroy_string += f"{key} x{new_destroy[key]}\n"

  #turns list of warnings to a string
  if warnings:
    warnings = "\n".join(warnings)

  #creates room object
  try:
    print("Keys being crteated:")
    print(new_keys)
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
    await ctx.reply(f"Error: There was a problem generating your room. Did you enter the data incorrectly? Ask Ironically-Tall for help if you're unsure.\nError:\n{e}", ephemeral=True)
    return
  dict = new_room.__dict__
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
    embed.add_field(name="Lock", value=f"{lock.replace(' ', '').split(',')}", inline=False)
  if unlock:
    embed.add_field(name="Unlock", value=f"{unlock.replace(' ', '').split(',')}", inline=False)
  if hide:
    embed.add_field(name="Hide", value=f"{hide.replace(' ', '').split(',')}", inline=False)
  if reveal:
    embed.add_field(name="Reveal", value=f"{reveal.replace(' ', '').split(',')}", inline=False)
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
  player = database.get_player(interaction.user.id)
  coauthors = None if not player else player["coauthor"]
  pattern = re.compile(re.escape(current), re.IGNORECASE)
  owned_adventures_query = database.adventures.find({"author": interaction.user.id})
  owned_adventures = [(adventure["name"], adventure["author"]) for adventure in owned_adventures_query]
  coauthored_adventures_query = database.adventures.find({"name": {"$in": coauthors}})
  coauthored_adventures = [(adventure["name"], adventure["author"]) for adventure in coauthored_adventures_query]
  all_adventures = owned_adventures + coauthored_adventures
  filtered_adventures = [
        (adventurename, author) for adventurename, author in all_adventures if pattern.search(adventurename)
    ]
  choices = [app_commands.Choice(name=f"{adventurename}", value=adventurename) for adventurename, _ in filtered_adventures[:25]]
  return choices

async def setup(bot):
  bot.add_command(newroom)