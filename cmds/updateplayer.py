import discord
from discord import app_commands
from discord.ext import commands

import database


#edits a player with whatever the user selects
@commands.hybrid_command(name="updateplayer", description="Edit player attributes. For admins only")
@app_commands.describe(
alive = "Whether the player is alive. True/False",
deaths="How many deaths the player has",
room="The room ID the player is currently playing in",
architect="Whether the player is an architect",
guild="The server ID where the player was created",
play_thread="The thread ID where the player is playing",
owned_adventures="List of adventures owned by the player",
coauthor="List of adventures where the player is allowed as coauthor",
history="The list of all the IDs the player has encountered",
keys="Lister of the keys and their amounts",
)
async def updateplayer(ctx, id : str,
  #giant block of arguments!
  alive : bool | None = None,
  deaths : int | None = None,
  room : str | None=None,
  architect : bool | None = None,
  guild : str | None = None,
  play_thread : str | None = None,
  owned_adventures : str | None = None,
  coauthor : str | None = None,
  history : str | None = None,
  keys : str | None = None,
                ):
  
  #checks if player is in database
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
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

  #warnings for any issues found
  warnings = []

  #error for no player found
  found_player = database.users.find_one({"disc": int(id)})
  if not found_player:
    await ctx.reply(f"Error: No player found with id **{id}**! Double check you've selected a valid ID.", ephemeral=True)
    return

  #parses keys into dict
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
    for key in keys:
      keys_string += f"{key} x{new_keys[key]}\n"

  #parses history into list
  history_string = ""
  new_history = []
  if history:
    new_history = history.split(',')
    for id in new_history:
      history_string += f"{id}\n"

  #parses owned adventures into list
  coauthor_string = ""
  new_coauthor = []
  if coauthor:
    new_coauthor = coauthor.split(',')
    for id in new_coauthor:
      coauthor_string += f"{id}\n"

  #parses owned adventures into list
  owned_string = ""
  new_owned = []
  if owned_adventures:
    new_owned = owned_adventures.split(',')
    for id in new_owned:
      owned_string += f"{id}\n"

  #casts guild to int
  new_guild = None
  if guild is not None:
    try:
      new_guild = int(guild)
    except Exception as e:
      await ctx.reply(f"Error: You must use a number for the guild ID.\n{e}", ephemeral=True)
      print(e)

  #casts play_thread to int
  new_play_thread = None
  if play_thread is not None:
    try:
      new_play_thread = int(play_thread)
    except Exception as e:
      await ctx.reply(f"Error: You must use a number for the play thread.\n{e}", ephemeral=True)
      print(e)


  new_dict = found_player.copy()
  embed = discord.Embed(title=f"Editing player: {found_player['displayname']}\nID: **{id}**", description="Review the changes and select a button below:")
  if alive is not None and alive != new_dict["alive"]:
    new_dict["alive"] = alive
    embed.add_field(name="Alive", value=f"**Old:**: {found_player['alive']}\n**New:** {alive}\n", inline=False)
  if deaths:
    new_dict["deaths"] = deaths
    embed.add_field(name="Deaths", value=f"**Old:** {found_player['deaths']}\n**New:** {deaths}", inline=False)
  if room:
    new_dict["room"] = room
    embed.add_field(name="Room", value=f"**Old:** {found_player['room']}\n**New:** {room}", inline=False)
  if architect is not None and architect != new_dict["architect"]:
    new_dict["architect"] = architect
    embed.add_field(name="Architect", value=f"**Old:** {found_player['architect']}\n**New:** {architect}", inline=False)
  if guild:
    new_dict["guild"] = new_guild
    embed.add_field(name="Guild", value=f"**Old:** {found_player['guild']}\n**New:** {guild}", inline=False)
  if play_thread:
    new_dict["play_thread"] = new_play_thread
    embed.add_field(name="Play Thread", value=f"**Old:**{found_player['play_thread']}\n**New:** {play_thread}", inline=False)
  if owned_adventures:
    new_dict["owned_adventures"] = new_owned
    embed.add_field(name="Owned Adventures", value=f"**Old:** {found_player['owned_adventures']}\n**New:** {owned_string}", inline=False)
  if coauthor:
    new_dict["coauthor"] = new_coauthor
    embed.add_field(name="Coauthor", value=f"**Old:** {found_player['coauthor']}\n**New:** {coauthor_string}", inline=False)
  if history:
    new_dict["history"] = new_history
    embed.add_field(name="History", value=f"**Old:**{found_player['history']}\n**New:** {history_string}", inline=False)
  if keys:
    old_keys = ""
    for key in found_player["keys"]:
      old_keys += f"{key} x{found_player['keys'][key]}\n"
    new_dict["keys"] = new_keys
  
  if not embed.fields:
    embed.description = "ERROR"
    embed.add_field(name="No changes", value="No changes were made. You need to select one of the options to edit the player. If you're unsure, try /help editkey")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  if warnings:
    embed.add_field(name="**WARNING**", value="\n".join(warnings), inline=False)
  edit_button = database.ConfirmButton(label="Make Changes", confirm=True, action="overwrite_player", id=id, dict=new_dict)
  cancel_button = database.ConfirmButton(label="Cancel", confirm=False, action="cancel", id=id)
  view = discord.ui.View()
  view.add_item(edit_button)
  view.add_item(cancel_button)
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(updateplayer)