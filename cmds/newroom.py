from discord.ext import commands
from discord import app_commands
import database
import formatter
import perms_ctx as permissions
import discord

#Makes a new room in the database
@commands.hybrid_command(name= "newroom", description= "Create a new room")
async def newroom(ctx, room_name : str, room_description : str):
  truename = ctx.author.id
  name = ctx.author.display_name
  player = database.get_player(truename)
  #cancel if they are not a player
  if not player:
    embed = formatter.embed_message(truename, "Error", "notplayer", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #cancel if they have no adventure to add a room to
  if not player["edit_thread"]:
    embed = formatter.blank_embed(name, "No Adventure", "You do not have an adventure to add a room to. You can create one with /newadventure.", "red")
    await ctx.reply(embed=embed, ephemeral=True)
    return
  #cancel if command was issued outside the proper thread
  if not permissions.correct_edit_thread(ctx):
    thread = ctx.guild.get_thread(player["edit_thread"])
    #checks if the thread exists in the guild
    if not thread:
      await ctx.reply("It looks like the thread you were using to edit your adventure has been deleted. A new thread is being created...", ephemeral=True)
      adventure = database.get_adventure_by_author(truename)
      #error for when the adventure is deleted from the database but not player
      if not adventure:
        await ctx.reply(f"Your adventure is missing from the databse. Please contact an admin. Adventure for '{truename}' not found!", ephemeral=True)
        return
      thread = await ctx.channel.create_thread(name=f"{name} editing {adventure['name']}")
      #creates a new thread, updates the player's edit thread
      await ctx.reply(f"A new thread has been created for you. Please re-use the command in {thread.mention} to edit your adventure.", ephemeral=True, suppress_embeds=True)
      database.update_player({"disc" : truename, "edit_thread": thread.id})
      return
  try:
    adventure = database.get_adventure_by_author(truename)
    if not adventure:
      await ctx.reply(f"Your adventure is missing from the databse. Please contact an admin.", ephemeral=True)
      return
    roomname = room_name
    desc = room_description
    select = discord.ui.Select(options=[
      discord.SelectOption(label="Regular Room", value="description", description="A regular room"),
      discord.SelectOption(label="Ending", value="name", description="A Room that ends the adventure")
    ])
    input = discord.ui.TextInput(label="Enter the new value", placeholder="Enter the new value", style=discord.TextStyle.paragraph)
    button = database.CreateRoomButton(label= "Create Room", roomname= roomname, roomdesc=desc, row=1)
    view = discord.ui.View()
    view.add_item(select)
    view.add_item(button)
    #modal for sending room data to database
    await ctx.reply(f"This will create a new Room in the adventure {adventure['name']}\n\nRoom Name:\n{roomname}\n\nRoom Description:\n{desc}\n(room description will be shown to the player when they enter that room)\n- You can add other things to the room once it is created.", view=view, ephemeral=True)
  except Exception as e:
    await ctx.reply(f"Error: {e}")
    print(e)

async def setup(bot):
  bot.add_command(newroom)