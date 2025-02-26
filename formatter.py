import discord

import database
from database import RoomButton

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
  "exitblocked": "you cannot go that way right now. Try exploring and finding an key that will allow you to pass.",
  "nokey": "Invalid combination! You must use !combine <#> <#> on two or more keys in your inventory. Use the key numbers as they appear in your inventory.",
  "emptyinventory": "You have no keys! Try this command again when you find an key.",
  "onlyonekey": "You must combine at least two keys like !combine <key> <key>. Please try again with at least two keys.",
  "nocombo": "Those keys do not all combine together.",
  "combo": "You sucsessfully combined the keys! The new key has been added to your inventory. You can !deconstruct it to get your old keys back.",
  "keydoesntexist": "CRITICAL ERROR - key does not exist!",
}

def embed_message(disc, title, description, color):
  description = disc + ", " + embed_messages[description]
  color = color_mapping.get(color, discord.Color.default())
  embed = discord.Embed(title=title, description=description, color=color)
  return embed

def blank_embed(disc, title, description, color):
  description = disc + ", " + description
  color = color_mapping.get(color, discord.Color.default())
  embed = discord.Embed(title=title, description=description, color=color)
  return embed

help_info = {
  "architect": "**/architect** - use this to see information about how to build adventures. You must be an architect to use this command.",
  "adventures": "**/adventures** - Shows all adventures that are currently available. You can join any adventure by using /join <advevnture name>.",
  "join" : "**/join <name_of_adventure>** - join an adventure if you aren't already playing. Use this command first, if you're new. You can only play one adventure at a time.",
  "leave" : "**/leave** - leave the game, erases player data.If you die you must leave the game to start a new one.",
  "inventory" : "**/inventory** - tells you what items you have. Not all adventures have items you can collect.",
  "journal": "**/journal** - Shows the journal of your adventure. Here you'll see a list of items you have collected, quests completed, and major events. Not all adventures have journal entries.",
  "combine" : "**/combine <item, item>** - tries to combine two or more items together", 
  "deconstruct" : "**/deconstruct** - tries to break an inventory item down",
  "help" : "**/help <command>** - displays additional help for a specified command.",
  "resend" : "**/resend** - Resends the current room information to the thread",
}

help_more_info = {
  "architect": "Architects are people who can build adventures. This command will give you information about how you can do that. If you want to become an architect, ask Ironically-Tall to get started.",
  "adventures": "Each adventure has unique rooms and endings. More adventures will be available in the future, as well as functionality to create your own. If you encounter an error during an adventure, let the author of the adventure or Ironically-Tall know.",
  "join" : " You must join an adventure before you can play. When you join an adventure you will start your story in a thread! Type the name of the adventure as it appears, capitalization doesn't matter. More adventures will be added in the future. You can only be in one adventure at a time.",
  "leave" : " Leaves the current adventure. This may clear errors from your player, but will erase all of your adventure data. You will need to /join again to resume playing. If you find a error where you must leave the game please screenshot the error and let Ironicall-Tall know.",
  "inventory" : "This will display all of the items you have collected on your adventure. Whoever wrote the adventure may not have added items. You might be able to combine items together, or break an item into other items depending on how the adventure was written. Your inventory starts empty, and you'll get a notification when you find an item.",
  "journal": "**/journal** - Your journal works like an inventory, but for nonphysical items. You might see the status of how much a character trusts you located here, or you might see the code to the door that is locked. Your journal starts empty, and you'll get a notification when something in it is added.",
  "combine" : " Not every item is part of a combination. In order to combine items correctly, you must /combine them and only them together. Some keys may hint at being able to be combined.", 
  "deconstruct" : "Break items into other items. Not all items can be broken down into smaller parts. Some items found in the adventure may start deconstructable.",
  "help" : " If you need more help than what this bot can provide, please contact Ironically-Tall. He created this bot, and it's his fault if something is wrong.",
  "resend" : "**/resend** - Sometimes the bot gets stuck and forgets what room you're in due to having a restart. You can use this command to ask it to resend the room you're in. If the issue does not resolve, contact Ironically-Tall",
}

def help(helpword):
  if helpword and helpword in help_more_info:
    embed = discord.Embed(title="**/" + helpword + "**", 
      description=help_more_info[helpword], color=discord.Color.blue())
    embed.set_footer(text="This bot was created by and is maintained by Ironically-Tall. Talk to him if you find any bugs!")
  else:
    embed = discord.Embed(title="Commands", 
    description=
    help_info["join"] + "\n" +
    help_info["leave"] + "\n" +
    help_info["adventures"] + "\n" +
    help_info["inventory"] + "\n" +
    help_info["combine"] + "\n" + 
    help_info["deconstruct"] + "\n" +
    help_info["help"] + "\n",
    color=discord.Color.blue())
    embed.set_footer(text="This bot was created by and is maintained by Ironically-Tall. Talk to him if you find any bugs!")
  return embed