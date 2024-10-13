import re

import discord
from discord import app_commands
from discord.ext import commands

import database


#edit advenure no longer applies
@commands.hybrid_command(name="editadventure", description="Edit adventure properties")
@app_commands.choices(attribute=[
  app_commands.Choice(name="Name", value="name"),
  app_commands.Choice(name="Starting Room", value="start"),
  app_commands.Choice(name="Description", value="description")])

async def editadventure(ctx, name: str, attribute: app_commands.Choice[str], value: str, epilogue : bool, ready :bool):
  # Retrieve adventure and verify author
  adventure = database.adventures.find_one({"name": name})
  if not adventure:
    await ctx.reply("Error: Adventure not found! Double check your adventure ID!", ephemeral=True)
    return
  if ctx.author.id == adventure.get("author"):
    embed, view = await database.confirm_embed(confirm_text=f"This will edit the {attribute.name} to:\n'{value}'\nThe epilogue will be set to {epilogue}", title="Confirm Adventure Edit", action="edit_adventure", channel=ctx.channel, id=name)
    players_in_adventure = database.get_players_in_adventure(name)
    if players_in_adventure:
      embed.add_field(name="Warning! Players are in this adventure!", value=f"Changing things while they're in it might cause issues for them, but the adventure will be fine. Players in this adventure: {str(players_in_adventure)}", inline=False)
    if not adventure["ready"] and ready:
      embed.add_field(name="Adventure Will be made ready!", value="Setting this adventure to 'ready' will make it visible and joinable by new players.", inline=False)
    if adventure["ready"] and not ready:
      embed.add_field(name="Adventure Will be made unready!", value="Setting this adventure to unready will make it invisible and unjoinable by new players. Players already in this adventure will remain.", inline=False)
    await ctx.reply(embed=embed, view=view, ephemeral=True)
    return
  else:
    await ctx.reply("You do not have permission to edit this adventure.", ephemeral=True)
    return

# Autocompletion for name parameter in editadventure
@editadventure.autocomplete('name')
async def autocomplete_adventure_name(interaction: discord.Interaction, current: str):
  # Query the database for adventure name, filtering by author and name
  adventures_query = database.adventures.find(
  {
  "author": interaction.user.id, 
  "name": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "name": 1,
  "_id": 0
  }
  )
  # Fetch up to 25 item IDs for the autocomplete suggestions
  adventure_names = [adventure["name"] for adventure in adventures_query.limit(25)]
  # Create choices for each suggestion
  return [app_commands.Choice(name=name, value=name) for name in adventure_names]

async def setup(bot):
  bot.add_command(editadventure)