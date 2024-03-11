from discord.ext import commands
from discord import app_commands
import discord
import database
import re
from room import Room

#edits a room with whatever the user selects
@commands.hybrid_command(name="newroom", description="Create a new room. Leave options blank to keep the default value.")
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
    destroy : str | None = None
                  ):
  new_room = Room(description=description, displayname=displayname, entrance=entrance, alt_entrance=alt_entrance, exits=exits, deathnote=deathnote, url=url, hidden=hidden, locked=locked, end=end, once=once, keys=keys, lock=lock, unlock=unlock, hide=hide, reveal=reveal, destroy=destroy)
  
  if not new_room:
    await ctx.reply(f"Error: There was a problem generating your room. Did you enter data in incorrectly?", ephemeral=True)
    return
  dict = new_room.__dict__
  embed = discord.Embed(title=f"New room: {dict['displayname']}\nID: **{id}** (automatically generated)", description="Review the new room and select a button below:")
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
 
  edit_button = database.ConfirmButton(label="Create Room", confirm=True, action="new_room", id=id, dict=dict)
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
  bot.add_command(newroom)