from enum import unique
import re

import discord
from discord import app_commands
from discord.ext import commands

import database
from key import Key


#edits a key with whatever the user selects
@commands.hybrid_command(name="newkey", description="Edit key attributes. Leave options blank to keep the default value.")
@app_commands.describe(
displayname="The name of the key, for inventory purposes only",
description="The description of an item, for inventory purposes only",
note="The text as it appears in the journal to players",
alt_note="For follow-up journal entries after the key is removed",
subkey1="A key that can be combined with other subkeys to make this key",
subkey2="A key that can be combined with other subkeys to make this key",
subkey3="A key that can be combined with other subkeys to make this key",
subkey4="A key that can be combined with other subkeys to make this key",
deconstruct="Whether the key can be turned into its subkeys with /deconstruct",
inventory="Whether the key will appear in an inventory",
journal="Whether the key will appear in a journal",
unique="If they player adds this to their inventory, they may not do so again",
repeating="Every time the player enters the room, the room will give them the key",
stackable="Whether The player may have more than one.")
async def newkey(ctx,
    #giant block of arguments!
    displayname : str="Default Key Name",
    description : str="Default Description",
    note : str | None=None,
    alt_note : str | None=None,
    subkeys : str | None = None,
    inventory : bool | None = None,
    journal : bool | None = None,
    unique : bool | None = None,
    repeating : bool | None = None,
    stackable : bool | None = None,
                  ):
  new_key = Key(displayname=displayname, description=description, 
subkeys=subkeys.replace(' ', '').split(',') if subkeys else None, inventory=inventory if inventory else False, 
journal=journal if journal else False, 
unique=unique if unique else False, 
repeating=repeating if repeating else False, 
stackable=stackable if stackable else False)

  if not new_key:
    await ctx.reply("Error: There was a problem generating your key object. Did you change a True/False value to something besides True/False?", ephemeral=True)
    return
  dict = new_key.__dict__
  embed = discord.Embed(title=f"New key: {dict['displayname']}\nID: **{id}** (automatically generated)", description="Review the new key and select a button below:")
  embed.add_field(name="Displayname", value=f"{displayname}", inline=False)
  embed.add_field(name="Description", value=f"{description}", inline=False)
  embed.add_field(name="Subkeys", value=f"{subkeys}", inline=False)
  embed.add_field(name="Inventory", value=f"{inventory}", inline=False)
  embed.add_field(name="Journal", value=f"{journal}", inline=False)
  embed.add_field(name="Unique", value=f"{unique}", inline=False)
  embed.add_field(name="Repeating", value=f"{repeating}", inline=False)
  embed.add_field(name="Stackable", value=f"{stackable}", inline=False)
  
  edit_button = database.ConfirmButton(label="Create Key", confirm=True, action="new_key", id=id, dict=dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)


async def setup(bot):
  bot.add_command(newkey)