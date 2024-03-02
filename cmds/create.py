import discord
from discord import app_commands
from discord.ext import commands

import database
import perms_ctx as permissions


#creation mode for adding anything new or editing rooms
#edits one adventure at a time
#works similar to join, creates a private thread
@commands.hybrid_command(name="create", description="Begins creation mode for an adventure")
async def create(ctx, adventure_name: str):
  #check if player can create an adventure
  #using architect as a role to check for now
  if not permissions.has_role(ctx, "architect") and not permissions.check_any_admin(ctx):
    await ctx.reply("You do not have permission to edit an adventure!", ephmeral=True)
    return
  name = ctx.author.display_name
  channel = ctx.channel
  all_adventures = database.get_adventures()
  database.pp(all_adventures)
  #if adventure name is not an available adventure name
  #checks if the name matches any of the adventure names
  if adventure_name not in [adv["nameid"] for adv in all_adventures]:
    embed = discord.Embed(title="Error - No Adventure", description="There's no adventure by that name. Refer to this list of available adventures to edit:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed, ephemral=True)
    return
  #if adventure name is an available adventure name
  else:
    thread = await channel.create_thread(name=name + " editing " + adventure_name)
    thread_channel = ctx.bot.get_channel(thread.id)
    tuple = await database.creation_mode(thread_channel)
    embed = tuple[0]
    view = tuple[1]
    await thread.send(ctx.author.mention + "This is create mode",embed=embed, view=view)

# Autocompletion function for adventure_name in join command
@create.autocomplete('adventure_name')
async def autocomplete_join(ctx, current: str):
    adventures_query = database.get_adventures()
    possible_adventures = [adv["nameid"] for adv in adventures_query if current.lower() in adv["nameid"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_adventures[:10]]

async def setup(bot):
  bot.add_command(create)