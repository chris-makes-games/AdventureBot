import discord
from discord.ui import View

import database
from database import RoomButton
from item import Item

color_mapping = {
  "red": discord.Color.red(),
  "green": discord.Color.green(),
  "blue": discord.Color.blue(),
  "orange": discord.Color.orange(),
  "purple": discord.Color.purple(),
  "yellow": discord.Color.yellow(),
}

embed_messages = {
  "newgame": "you wake up in an unfamilliar place. The shiny hard floor underneath your feet stretches off into the horizon in a neat square grid. Between each square is a large grey divet about as deep as you are tall, and in the distance you can see walls miles high. You are incredilby small, stranded on the floor of an impossibly large kitchen.\nTo begin playing, try !info to look around the room you're in. For more commands, try !help",
  "alreadyplayer": "You are already playing in an adventure. !leave that one before trying to join another one.",
  "alreadyadventure": "You are already in an adventure. You must /leave that one before trying to join another one.",
  "noadventure" : "There is no adventure by that name. Please try again.",
  "joinsuccess": "you have been added! A new game was started in the test adventure. More adventures can be written later! Try !info to get started or !help for more commands.",
  "leavesuccess": "You have been removed from the adventure. Use !join <adventure name here> to start another.",
  "notplayer": "you are not a player. Try /newplayer if you are a new player",
  "notsarnt": "only Ironically-Tall can make new architects. Ask him.",
  "notarchitect": "you are not an architect. That command is only for people with that role. Talk to a moderator if you are interested.",
  "alreadyarchitect": "that user is already an architect!",
  "needuser": "you need to specify a user to make an architect.\nTry !architect <username @mention>",
  "newarchitect": "User has successfully been made an architect.",
  "dead": "you have reached a game over. Try !newgame to begin again. ",
  "noroom": "CRITICAL ERROR - Player is inside invalid room!",
  "noguild": "CRITICAL ERROR - Player is in invalid guild!",
  "exitformat": "wrong format for taking a path! Use !path <#>",
  "exitblocked": "you cannot go that way right now. Try exploring and finding an item that will allow you to pass.",
  "noitem": "Invalid combination! You must use !combine <#> <#> on two or more items in your inventory. Use the item numbers as they appear in your inventory.",
  "emptyinventory": "You have no items! Try this command again when you find an item.",
  "onlyoneitem": "You must combine at least two items like !combine <item> <item>. Please try again with at least two items.",
  "nocombo": "Those items do not all combine together.",
  "combo": "You sucsessfully combined the items! The new item has been added to your inventory. You can !deconstruct it to get your old items back.",
  "itemdoesntexist": "CRITICAL ERROR - Item does not exist!",
}

def embed_message(disc, title, description, color):
  description = disc + ", " + embed_messages[description]
  color = color_mapping.get(color, discord.Color.default())
  embed = discord.Embed(title=title, description=description, color=color)
  return embed

def button_test():
  button1 = RoomButton(label="Path 1", destination="test destination")
  button2 = RoomButton(label="Path 2", destination="test destination")
  test_view = View()
  test_view.add_item(button1)
  test_view.add_item(button2)
  return test_view

def button_text_test(text):
  print(text)

def blank_embed(disc, title, description, color):
  description = disc + ", " + description
  color = color_mapping.get(color, discord.Color.default())
  embed = discord.Embed(title=title, description=description, color=color)
  return embed

#used to send the player information about the room they are in
def embed_room(all_items, new_items, title, room, color):
  color = color_mapping.get(color, discord.Color.default())
  embed = discord.Embed(title=title, description=room["description"], color=color)
  view = discord.ui.View()
  if new_items:
    for item in new_items:
      found_item = database.get_item(item)
      description = found_item["description"] if found_item else "ERROR - ITEM HAS NO NAME"
      embed.add_field(name="You found an item:", value=description, inline=False)
  if len(room["exits"]) == 0:
    embed.add_field(name="Exits", value="There are no exits from this room. This is the end of the line. Unless this room is broken?", inline=False)
  if len(room["exits"]) == 1:
    embed.add_field(
    name="This area has only one way out.", value="Use !path 1 to take it.", inline=False)
  else:
    embed.add_field(name="Choose a Path:", value="Make your choice by clicking a button below:", inline=False)
  r = 1
  for exit in room["exits"]:
    if room["secrets"][r - 1] == "Open":
      button = RoomButton(label=str(exit), destination=room['exit_destination'][r - 1], row = r)
      view.add_item(button)
    elif room["secrets"][r - 1] == "Secret":
      if room["unlockers"][r - 1] in all_items:
        button = RoomButton(label=str(exit), destination=room['exit_destination'][r - 1], row = r)
        view.add_item(button)
    elif room["unlockers"][r - 1] in all_items:
      button = RoomButton(label=str(exit), destination=room['exit_destination'][r - 1], row = r)
      view.add_item(button)
    else:
      button = RoomButton(label=room["secrets"][r - 1], destination=room['exit_destination'][r - 1], disabled=True, row = r)
      view.add_item(button)
    r += 1
  return (embed, view)

def inventory(items):
  if items:
    if len(items) == 1:
      description = "You have only one item:"
    else:
      description = "These are the items you currently have. You can usually only take an item from a room once, and you cannot have duplicate items. Try !combine <#> <#> to create a new item using two or more items. You can also try !deconstruct <item> to break down an item into its components. You can also use !discard <#> to get rid of an item."
    embed = discord.Embed(title="Inventory", description=description, color=discord.Color.blue())
    n = 1
    for item in items:
      new_item = database.get_item(item)
      if new_item is None:
        name = "ERROR"
        description = "INVALID ITEM NAME/DESCRIPTION"
      else:
        name = str(n) + " - " + new_item["displayname"]
        description = new_item["description"]
        n += 1
      embed.add_field(name=name, value=description, inline=False)
  else:
    embed = discord.Embed(title="No Items", description="You have no items in your inventory", color=discord.Color.red())
  return embed

help_info = {
  "join" : "**!join <name_of_adventure>** - join an adventure if you aren't playing. Use this command first, if you're new. You can only play one adventure at a time.",
  "leave" : "**/leave** - leave the game, erases player data.If you die you must leave the game to start a new one.",
  "info" : "**/info** - gets information about where you are in the adventure and gives you information about where to go next.",
  "inventory" : "**/inventory** - tells you what items you have",
  "combine" : "**!combine <item, item>** - tries to combine two or more items", 
  "deconstruct" : "**!deconstruct <item number>** - tries to break an item down",
  "adventures" : "**/adventures** - gives you a list of available adventures",
  "help" : "**!help <command>** - displays detailed help for a command",
}

help_more_info = {
  "join" : " You must join an adventure before you can play. When you join an adventure you will start your story in a thread! Type the name of the adventure as it appears, capitalization doesn't matter. More adventures will be added in the future",
  "leave" : " This may clear errors from your player, but will erase all of your player data. You will need to !join again to resume playing. If you find a error where you must leave the game please screenshot the error for developers.",
  "adventures": "Each adventure has unique rooms and endings. More adventures will be available in the future, as well as functionality to create your own.",
  "info" : " It will tell you which paths are available, and describe the current scene. This command is useful if you need to resent the embed in your thread. Please do not use this command in the main channel.",
  "inventory" : " Your inventory is organized by number. You can perform actions on the items in your inventory by their number. You can only have one of each item, and most items can only be picked up once. Please do not use this command in the main channel.",
  "combine" : " Not every item is part of a combination. In order to combine items correctly, you must !combine them and only them together. Some items may hint at being able to be combined. Once combined, items can usually be broken down into the original parts with !deconstruct.Please do not use this command in the main channel.", 
  "deconstruct" : " Not all items can be broken down into smaller parts. Some items found in the adventure may start deconstructable. Most items you !combine will be deconstructable back to their original parts.Please do not use this command in the main channel.",
  "help" : " If you need more help than what this bot can provide, please contact Ironically-Tall or ❀LILLY❀. They created this bot, and it's their fault if something is wrong.",
}

def help(helpword):
  if helpword in help_more_info:
    embed = discord.Embed(title="**!" + helpword + "**", 
      description=help_more_info[helpword], color=discord.Color.blue())
    embed.set_footer(text="This bot was created by and is maintained by Ironically-Tall and ❀LILLY❀. Talk to them if you find any bugs!")
  else:
    embed = discord.Embed(title="Commands", 
    description=
    help_info["join"] + "\n" +
    help_info["leave"] + "\n" +
    help_info["adventures"] + "\n" +
    help_info["info"] + "\n" +
    help_info["inventory"] + "\n" +
    help_info["combine"] + "\n" + 
    help_info["deconstruct"] + "\n" +
    help_info["help"] + "\n",
    color=discord.Color.blue())
    embed.set_footer(text="This bot was created by and is maintained by Ironically-Tall and ❀LILLY❀. Talk to them if you find any bugs!")
  return embed