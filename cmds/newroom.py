import discord
from discord import app_commands
from discord.ext import commands

import database
from room import Room


#edits a room with whatever the user selects
@commands.hybrid_command(name="newroom", description="Create a new room. Leave options blank to keep the default value")
@app_commands.describe(displayname="The title of the room displayed to players",
description="Second-person description of the room displayed to players",
entrance="Description of a choice that leads to this room",
alt_entrance="Description of the choice when the room is blocked and cannot be selected",
exits="IDs of other rooms that this room can exit to. Separate with commas",
deathnote="For endings that kill the player, describe how they died. No pronouns",
url= "URL to an image to display in the room next to the description",
hidden= "This room will not appear as a choice unless the player has the keys in 'reveal'",
locked= "The choice for this room will be alt_text and be unselectable unless player has keys in 'unlock'",
end= "Room that ends the adventure. Include a deathnote if the ending is a death",
once= "If the player selects the option to go into this room, the option to do so will not appear again",
keys= "Keys that will be given to the player when they enter the room, if they can recieve them",    
lock= "IDs of keys that will lock this room if they player has them. Separate by commas",  
unlock= "Keys required to unlock the room. Separate by commas",  
hide= "IDs of keys that will make this room hidden if the player has them. Separate by commas",  
reveal= "Keys required to reveal the room. Separate by commas",  
destroy= "Keys that will be removed from the player if they enter this room. Separate by commas")
async def newroom(ctx,
    #giant block of arguments!
    displayname : str= "Room Name",
    description : str="You're reading a default description for an empty room",
    entrance : str="Go into the new room",
    alt_entrance : str="The path into the new room is blocked!",
    exits : str | None = None,
    deathnote : str="killed in the new room",
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
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer before trying to make a new room.", ephemeral=True)
    return
  #need to rework this check/logic
  adventure_of_room = "Error: Unknown Adventure"
  if player["edit_thread"]:
    adventure_of_room = player["edit_thread"][1]
  new_id = database.generate_unique_id()
  new_room = Room(id=new_id, description=description, displayname=displayname, entrance=entrance, alt_entrance=alt_entrance, exits=exits, deathnote=deathnote, url=url, hidden=hidden, locked=locked, end=end, once=once, keys=keys, lock=lock, unlock=unlock, hide=hide, reveal=reveal, destroy=destroy, author=ctx.author.id, adventure=adventure_of_room)
  
  if not new_room:
    await ctx.reply("Error: There was a problem generating your room. Did you enter the data incorrectly? Ask Ironically-Tall for help if you're unsure.", ephemeral=True)
    return
  dict = new_room.__dict__
  embed = discord.Embed(title=f"New room: {dict['displayname']}\nID: **{new_id}** (automatically generated)\nAny room attributes not specified have been left at their default values.", description="Review the new room and select a button below:")
  embed.add_field(name="Displayname", value=f"{displayname}", inline=False)
  embed.add_field(name="Description", value=f"{description}", inline=False)
  embed.add_field(name="Entrance", value=f"{entrance}", inline=False)
  embed.add_field(name="Alt Entrance", value=f"{alt_entrance}", inline=False)
  embed.add_field(name="Exits", value=f"{exits}", inline=False)
  embed.add_field(name="Deathnote", value=f"{deathnote}", inline=False)
  embed.add_field(name="URL", value=f"{url}", inline=False)
  embed.add_field(name="Keys", value=f"{keys}", inline=False)
  embed.add_field(name="Hidden", value=f"{hidden}", inline=False)
  embed.add_field(name="Locked", value=f"{locked}", inline=False)
  embed.add_field(name="End", value=f"{end}", inline=False)
  embed.add_field(name="Once", value=f"{once}", inline=False)
  embed.add_field(name="Lock", value=f"{lock}", inline=False)
  embed.add_field(name="Unlock", value=f"{unlock}", inline=False)
  embed.add_field(name="Hide", value=f"{hide}", inline=False)
  embed.add_field(name="Reveal", value=f"{reveal}", inline=False)
  embed.add_field(name="Destroy", value=f"{destroy}", inline=False)

  edit_button = database.ConfirmButton(label="Create Room", confirm=True, action="new_room", dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel")
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(newroom)