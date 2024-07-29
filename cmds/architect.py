import formatter

import discord
from discord import app_commands
from discord.ext import commands


#command for architect details about creating content
#works like help command but for architects
@commands.hybrid_command()
async def architect(ctx, command=None):
  if command:
    command = command.lower()
  if not command:
    embed = discord.Embed(title="Architect Information", description="Architects are able to create thier own adventures. You can read about how to do that here. If you have more specific questions about how things work, try /architect <topic> for one of the topics below. Feel free to ask Ironically-Tall if you still have questions.", color=discord.Color.yellow())
    embed.add_field(name="Adventures", value="Everything you create will be stored in an adventure. An adventure is a list of rooms, and rooms can contain various keys. You can only create one adventure, and someone can only play one adventure at a time. People can play adventures more than once.")
    embed.add_field(name="Rooms", value="Rooms are the primary vehicle by which the game is delivered to players. Here the information and description of the environment is given to players, and players are given choices about which room to enter next. Rooms are connected together in a variety of ways, and can be restricted to requiring certain keys to enter. Rooms need not be literal rooms, and can include just about anything you can think of. Consider rooms to be like a 'page' of the adventure story.")
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
    embed.add_field(name="Display Name", value="This is the title of the room as displayed to players. When a player enters a room, this will be at the top of the message. Usually written in second person but not necessarily.")
    embed.add_field(name="Description", value="This is the meat and potatoes of all adventures. This is where you describe the environment and give the player choices about what to do next. Usually written in second person. You can use discord formatting here like italics, bold, and links. If you want to use a newline, you must use the special character: \\n")
    embed.add_field(name="Entrance", value="This is what is displayed when this room is an option to select from another room. At the bottom of rooms, all rooms which can be selected are displayed. The entrance text for that destination room will normally be displayed unless the room is hidden or locked.")
    embed.add_field(name="Alt_Entrance", value="When a room is locked, this text is displayed instead of the entrance text. The button to select it will not be clickable, but the player will be made aware of a possible future option.")
    embed.add_field(name="Hidden", value="True/False. Hidden rooms will not display their entrance buttons to be travelled to from other rooms, and will remain so until their reveal parameters are met.")
    embed.add_field(name="Locked", value="True/False. Locked rooms will have their alt_entrance displayed and be unselectable unless their unlock parameters are met.")
    embed.add_field(name="End", value="True/False. If marked true, this room will end the adventure. Once ended, the adventure will no longer be playable unless the adventure epilogue is true. If the ending involves the player dying, the deathnote will be displayed to all players. Players reaching an ending room will count towards the adevnture total plays.")
    embed.add_field(name="Once", value="True/False. If true, this room can only be entered once. The player may recieve the option to enter the room more than once, but if they player selects this room then the option will not appear again.")
    embed.add_field(name="Keys", value="A list of the keys which are given to the player upon entering the room. Keys have properties which may prevent themselves from being given to the player. Type the ID of the key then a space and then the amount of that key to be given. Separate by commas.\nExample:\n`keyid1 2, keyid2 3`\nThis will attempt to give two keyid1's to the player and 3 of keyid2.\ntry /architect keys for more information.")
    embed.add_field(name="Destroy", value="Similar but opposite to keys. List of keys which are destroyed when the player enters the room. If the player does not have the keys, nothing happens. Each time the player enters the room, that ammount of those keys will be destroyed. Separate by commas.\nExample:\n`keyid1 2, keyid2 3`\nThis will attempt to destroy two keyid1's in the player's inventory and 3 of keyid2.")
    embed.add_field(name="Exits", value="A list of rooms which can be accessed from this room. Each exit is a room ID. Rooms listed as exits here will display their entrance text as buttons at the bottom of this room. Separate by commas. Maximum 4 exits.\nExample:\n`roomid1, roomid2`")
    embed.add_field(name="Unlock", value="Logical expression. If this expression is true, the room will be unlocked. If the room is not locked, this will do nothing. The expression should contain key IDs using operators and parentheses. Operators: Or, And, Not, >, <, =, <=, >=\nExample:\n`(key1 = 4 or key2 > 5) and key3 >= 1`\nThis will unlock the room if the player has exactly 4 of key1 or more than 5 of key2 and at least 1 of key3.")

  else:
    embed = formatter.help(command)


  await ctx.reply(embed=embed, ephemeral=True)

@architect.autocomplete("command")
async def autocomplete_help(interaction: discord.Interaction, current: str):
  all_commands = ["Adventures", "Rooms", "Keys", "Journal", "Inventory"]
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(architect)