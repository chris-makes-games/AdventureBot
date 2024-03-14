import re

import discord
from discord import app_commands
from discord.ext import commands

import database


#edits a room with whatever the user selects
@commands.hybrid_command(name="editroom", description="Edit room attributes. Leave options blank to keep the current value")
async def editroom(ctx, id: str,
    #giant block of optional arguments!
    description : str | None = None,
    displayname : str | None = None,
    entrance : str | None = None,
    alt_entrance : str | None = None,
    exits : str | None = None,
    deathnote : str | None = None,
    url : str | None = None,
    keys : str | None = None,
    hidden : bool | None = None,
    locked : bool | None = None,
    end : bool | None = None,
    once : bool | None = None,
    lock : str | None = None,
    unlock : str | None = None,
    hide: str | None = None,
    reveal : str | None = None,
    destroy : str | None = None
                  ):
  found_room = database.rooms.find_one({"id": id})
  if not found_room:
    await ctx.reply(f"Error: No room found with id **{id}**! Double check the ID, you should just select a room from the list. If you're sure it should be correct, contact Ironically-Tall", ephemeral=True)
    return
  new_dict = found_room.copy()
  embed = discord.Embed(title=f"Editing room: {found_room['displayname']}\nID: **{id}**", description="Review the changes and select a button below:")
  if description:
    new_dict["description"] = description
    embed.add_field(name="Description", value=f"Old: {found_room['description']}\nNew: {description}", inline=False)
  if displayname:
    new_dict["displayname"] = displayname
    embed.add_field(name="Displayname", value=f"Old: {found_room['displayname']}\nNew: {displayname}", inline=False)
  if entrance:
    new_dict["entrance"] = entrance
    embed.add_field(name="Entrance", value=f"Old: {found_room['entrance']}\nNew: {entrance}", inline=False)
  if alt_entrance:
    new_dict["alt_entrance"] = alt_entrance
    embed.add_field(name="Alt Entrance", value=f"Old: {found_room['alt_entrance']}\nNew: {alt_entrance}", inline=False)
  if exits:
    new_dict["exits"].append(exits)
    embed.add_field(name="Exits", value=f"Old: {found_room['exits']}\nNew: {exits}", inline=False)
  if deathnote:
    new_dict["deathnote"] = deathnote
    embed.add_field(name="Deathnote", value=f"Old: {found_room['deathnote']}\nNew: {deathnote}", inline=False)
  if url:
    new_dict["url"] = url
    embed.add_field(name="URL", value=f"Old: {found_room['url']}\nNew: {url}", inline=False)
  if keys:
    new_dict["keys"].append(keys)
    embed.add_field(name="Keys", value=f"Old: {found_room['keys']}\nNew: {keys}", inline=False)
  if hidden:
    new_dict["hidden"] = hidden
    embed.add_field(name="Hidden", value=f"Old: {found_room['hidden']}\nNew: {hidden}", inline=False)
  if locked:
    new_dict["locked"] = locked
    embed.add_field(name="Locked", value=f"Old: {found_room['locked']}\nNew: {locked}", inline=False)
  if end:
    new_dict["end"] = end
    embed.add_field(name="End", value=f"Old: {found_room['end']}\nNew: {end}", inline=False)
  if once:
    new_dict["once"] = once
    embed.add_field(name="Once", value=f"Old: {found_room['once']}\nNew: {once}", inline=False)
  if lock:
    new_dict["lock"].append(lock)
    embed.add_field(name="Lock", value=f"Old: {found_room['lock']}\nNew: {lock}", inline=False)
  if unlock:
    new_dict["unlock"].append(unlock)
    embed.add_field(name="Unlock", value=f"Old: {found_room['unlock']}\nNew: {unlock}", inline=False)
  if hide:
    new_dict["hide"].append(hide)
    embed.add_field(name="Hide", value=f"Old: {found_room['hide']}\nNew: {hide}", inline=False)
  if reveal:
    new_dict["reveal"].append(reveal)
    embed.add_field(name="Reveal", value=f"Old: {found_room['reveal']}\nNew: {reveal}", inline=False)
  if destroy:
    new_dict["destroy"].append(destroy)
    embed.add_field(name="Destroy", value=f"Old: {found_room['destroy']}\nNew: {destroy}", inline=False)
  if not embed.fields:
    embed.description = "ERROR"
    embed.add_field(name="No changes", value="No changes were made. You need to select one of the options to edit the room. If you're unsure, try /help editroom")
    await ctx.reply(embed=embed, ephemeral=True)
    return
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