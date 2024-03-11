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
    await ctx.reply("You do not have permission to edit an adventure!", ephemeral=True)
    return
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("You are not registered as a player! You must use /newplayer to begin", ephemeral=True)
    return
  if player and player["edit_thread"]:
    thread = ctx.guild.get_channel_or_thread(player["edit_thread"])
    if not thread:
      await ctx.reply("It looks like you were editing an adventure in a channel that no longer exists. Your old editing thread is being closed...", ephemeral=True)
      player.update({"edit_thread": None})
      database.update_player(player)
    else:
      message_link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}/{thread.last_message_id}"
      await ctx.reply(f"You are already in the middle of editing an adventure! Click here to go there:\n{message_link}\nIf the link is broken, contact a moderator!", ephemeral=True, suppress_embeds=True)
      return
  displayname = ctx.author.display_name
  channel = ctx.channel
  all_adventures = list(database.get_adventures())
  #if adventure name is not an available adventure name
  #checks if the name matches any of the adventure names
  if adventure_name not in [adv["name"] for adv in all_adventures]:
    embed = discord.Embed(title="Error - No Adventure", description="There's no adventure by that name. Refer to this list of available adventures to edit:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["name"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #if adventure name is an available adventure name
  else:
    thread = await channel.create_thread(name=displayname + " editing " + adventure_name)
    thread_channel = ctx.bot.get_channel(thread.id)
    tuple = await database.creation_mode(thread_channel)
    embed = tuple[0]
    view = tuple[1]
    await thread.send(ctx.author.mention + "Create mode started:",embed=embed, view=view)
    message_link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"
    await ctx.reply(f"You have begun creation mode for **{adventure_name.title()}**! Go to the new thread to begin:\n{message_link}", ephemeral=True , suppress_embeds=True)
    player = database.get_player(ctx.author.id)
    if player:
      player.update({"edit_thread": thread.id})
      database.update_player(player)

# Autocompletion function for adventure_name in join command
@create.autocomplete('adventure_name')
async def autocomplete_join(interaction: discord.Interaction, current: str):
    adventures_query = database.get_adventures()
    possible_adventures = [adv["name"] for adv in adventures_query if current.lower() in adv["name"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_adventures[:10]]

async def setup(bot):
  bot.add_command(create)