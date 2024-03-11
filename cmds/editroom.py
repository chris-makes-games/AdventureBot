from discord.ext import commands
from discord import app_commands
import discord
import database
import re

#edits a room with whatever the user selects
@commands.hybrid_command(name="editroom", description="Edit room attributes. Leave options blank to keep the current value.")
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
    await ctx.reply(f"Error: No room found with id {id}!", ephemeral=True)
    return
  embed = discord.Embed(title=f"Editing room {id}", description="These edits were made:")
  if description:
    embed.add_field(name="Description", value=f"Old: {found_room['description']}\nnew: {description}", inline=False)
  if displayname:
    embed.add_field(name="Displayname", value=f"Old: {found_room['displayname']}\nnew: {displayname}", inline=False)
  if entrance:
    embed.add_field(name="Entrance", value=f"Old: {found_room['entrance']}\nnew: {entrance}", inline=False)
  if alt_entrance:
    embed.add_field(name="Alt Entrance", value=f"Old: {found_room['alt_entrance']}\nnew: {alt_entrance}", inline=False)
  if exits:
    embed.add_field(name="Exits", value=f"Old: {found_room['exits']}\nnew: {exits}", inline=False)
  if deathnote:
    embed.add_field(name="Deathnote", value=f"Old: {found_room['deathnote']}\nnew: {deathnote}", inline=False)
  await ctx.reply(embed=embed, ephemeral=True)

#returns rooms with matching is OR matching displayname
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