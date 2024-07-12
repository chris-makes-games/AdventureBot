import formatter

import discord
from discord import app_commands
from discord.ext import commands

import database


#basic help command, replies with embed
#allows the user to optionally /help other commands
#will only autocomplete with commands that the user has permission to use
@commands.hybrid_command()
async def architect(ctx, command=None):
  if command:
    command = command.lower()
  if not command:
    embed = discord.Embed(title="Architect Information", description="Architects are able to create thier own adventures. You can read about how to do that here. If you have more specific questions about how things work, try /architect <topic> for one of the topics below. Feel free to ask Ironically-Tall if you still have questions.", color=discord.Color.yellow())
    embed.add_field(name="Adventures", value="Everything you create will be stored in an adventure. An adventure is a list of rooms, and rooms can contain various keys. You can only create one adventure, and someone can only play one adventure at a time. People can play adventures more than once.")
    embed.add_field(name="Rooms", value="Rooms are the primary vehicle by which the game is delivered to players. Here the information and description of the environment is given to players, and players are given choices about which room to enter next. Rooms are connected together in a variety of ways, and can be restricted to requiring certain keys to enter. Rooms need not be literal rooms, and can include just about anything you can think of. Consider rooms to be a 'page' of the adventure.")
    embed.add_field(name="Keys", value="Keys are ways to track how players are progressing through the adventure. The adventure does not change, nor do the rooms change. The keys the player has change, which may change which rooms are available to the player. Keys need not be literal keys which unlock rooms, but can be conecpts like the favor of an NPC. Keys can optionally be shown to the player, in their journal or inventory or both.")
    embed.add_field(name="Journal", value="The Journal is a way for the player to read about their keys. Keys must have the journal field set to true to be read here. Keys can instead be invisible, used only by the adventure to track progress. ")
    embed.add_field(name="Inventory", value="The Inventory is another way for the player to read about their keys. These kinds of keys are meant to be physical items the player collects along their way. These items can optionally also have a journal entry. Keys can optionally be combined together or deconstructed by the player if they are inventory items.")
  elif command == "adventures":
    embed = discord.Embed(title="Adventures Additional Info", description="Everything you create will be stored in an adventure. An adventure is a list of rooms, and rooms can contain various keys. You can only create one adventure, and someone can only play one adventure at a time. People can play adventures more than once.")
    embed.add_field(name="Creating an Adventure", value="Use /newadventure to start writing a new adventure. A thread will be generated for you to write commands to edit that adventure. A starting room will automatically be created for you, which you can edit. All rooms and keys you create will be added to the adventure.")
    embed.add_field(name="Word Count and Total Plays", value="When someone uses the /adventures command, the total words of the rooms in your adventure will be counted to be displayed. Whenever a player reaches a room marked 'end', the total plays will increment by one.")
  elif command == "rooms":
    embed = discord.Embed(title="Rooms Additional Info", description="Rooms are the primary vehicle by which the game is delivered to players. Here the information and description of the environment is given to players, and players are given choices about which room to enter next. Rooms are connected together in a variety of ways, and can be restricted to requiring certain keys to enter. Rooms need not be literal rooms, and can include just about anything you can think of. Consider rooms to be a 'page' of the adventure.")
    embed.add_field(name="Creating a Room", value="Use /newroom to start writing a new room. You can /editroom that room later. You do not need to specify anything to create a room, and all the fields will default to empty or False.")
    embed.add_field(name="Room ID", value="This is the unique ID of the room. It is used to reference the room in commands. You can specify an ID for the room or leave this blank and a random ID will be generated. IDs cannot be duplicated across any room that any player has put in any adventure.")
    embed.add_field(name="Room Display Name", value="This is the title of the room as displayed to players. When a player enters a room, this will be at the top of the message. Usually written in second person but not necessarily.")
    embed.add_field(name="Room Description", value="This is the meat and potatoes of all adventures. This is where you describe the environment and give the player choices about what to do next. Usually written in second person. You can use discord formatting here like italics, bold, and links. If you want to use a newline, you must use the special character: \\n.")

  else:
    embed = formatter.help(command)


  await ctx.reply(embed=embed, ephemeral=True)

@architect.autocomplete("command")
async def autocomplete_help(interaction: discord.Interaction, current: str):
  all_commands = database.get_architect_commands()
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(architect)