import discord
from discord import app_commands
from discord.ext import commands

import database

#command for architect details about creating content
#works like help command but for architects
@commands.hybrid_command(name= "architecthelp", description= "Help for architects to make adventures")
@app_commands.describe(topic = "Optionally specify a specific architect topic")
async def architecthelp(ctx, topic=None):
  #makes sure bot command is in registered channel
  if not database.check_channel(ctx.channel.id, ctx.guild.id):
    guild_info = database.botinfo.find_one({"guild" : ctx.guild.id})
    if guild_info:
      await ctx.reply(f"This command can only be used approved bot channels! Use this channel:\nhttps://discord.com/channels/{ctx.guild.id}/{guild_info['channel']}", ephemeral=True)
      return
    else:
      await ctx.reply("This command can only be used approved bot channels! No channel found in this guild, try using `/register` as an admin.", ephemeral=True)
      return
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply("ERROR: You are not registered with the database. Please use /newplayer to begin.", ephemeral=True)
    return
  if topic:
    topic = topic.lower()
  if not topic:
    #basic info if no topic specified
    embed = discord.Embed(title="Architect Help", description="Architects are able to create thier own adventures. You can read about how to do that here. If you have more specific questions about how things work, try /architect <topic> for one of the topics below. Feel free to ask Ironically-Tall if you still have questions.", color=discord.Color.yellow())
    embed.add_field(name="Adventures", value="Everything you create will be stored in an adventure. An adventure is a list of rooms, and rooms can contain various keys. You can only create one adventure, and someone can only play one adventure at a time. People can play adventures more than once.")
    embed.add_field(name="Rooms", value="Rooms are the primary vehicle by which the game is delivered to players. Here the information and description of the environment is given to players, and players are given choices about which room to enter next. Rooms are connected together in a variety of ways, and can be restricted to requiring certain keys to enter. Rooms need not be literal rooms, and can include just about anything you can think of. Consider rooms to be like a 'page' of the adventure story.")
    embed.add_field(name="Keys", value="Keys are ways to track how players are progressing through the adventure. The adventure does not change, nor do the rooms change. The keys the player has change, which may change which rooms are available to the player. Keys need not be literal keys which unlock rooms, but can be conecpts like the favor of an NPC. Keys can optionally be shown to the player, in their journal or inventory or both.")
    embed.add_field(name="Journal", value="The Journal is a way for the player to read about their keys. Keys must have the journal field set to true to be read here. Keys can instead be invisible, used only by the adventure to track progress. ")
    embed.add_field(name="Inventory", value="The Inventory is another way for the player to read about their keys. These kinds of keys are meant to be physical items the player collects along their way. These items can optionally also have a journal entry. Keys can optionally be combined together or deconstructed by the player if they are inventory items.")
  #for adventure information
  elif topic == "adventures":
    embed = discord.Embed(title="Adventures Additional Info", description="Everything you create will be stored in an adventure. An adventure is a list of rooms, and rooms can contain various keys. You can only create one adventure, and someone can only play one adventure at a time. People can play adventures more than once.")
    embed.add_field(name="Creating an Adventure", value="Use /newadventure to start writing a new adventure. A thread will be generated for you to write commands to edit that adventure. A starting room will automatically be created for you, which you can edit. All rooms and keys you create will be added to the adventure.")
    embed.add_field(name="Word Count and Total Plays", value="When someone uses the /adventures command, the total words of the rooms in your adventure will be counted to be displayed. Whenever a player reaches a room marked 'end', the total plays will increment by one.")
  #for room information
  elif topic == "rooms":
    embed = discord.Embed(title="Rooms Additional Info", description="Rooms are the primary vehicle by which the game is delivered to players. Here the information and description of the environment is given to players, and players are given choices about which room to enter next. Rooms are connected together in a variety of ways, and can be restricted to requiring certain keys to enter. Rooms need not be literal rooms, and can include just about anything you can think of. Consider rooms to be a 'page' of the adventure.")
    embed.add_field(name="Creating a Room", value="Use /newroom to start writing a new room. You can /editroom that room later. You do not need to specify anything to create a room, and all the fields will default to empty or False.")
    embed.add_field(name="Room ID", value="This is the unique ID of the room. It is used to reference the room in commands. You can specify an ID for the room or leave this blank and a random ID will be generated. IDs cannot be duplicated across any room that any player has put in any adventure.")
    embed.add_field(name="Display Name", value="This is the title of the room as displayed to players. When a player enters a room, this will be at the top of the message. Usually written in second person but not necessarily.")
    embed.add_field(name="Description", value="This is the meat and potatoes of all adventures. This is where you describe the environment and tell them what happened based on their choice. They then use that information to decide what to do next. Usually written in second person. You can use discord formatting here like italics, bold, and links. If you want to use a newline, you must use the special character: `\\n`")
    embed.add_field(name="Entrance", value="This is what is displayed when this room is an option to select from another room. All rooms that connect to the room are displayed as buttons on the bottom of the room, with this text in that button. The entrance text for that destination room will normally be displayed unless the room is hidden or locked.")
    embed.add_field(name="Alt_Entrance", value="When a room is locked, this text is displayed instead of the entrance text. The button to select it will not be clickable, but the player will be made aware of a possible future option.")
    embed.add_field(name="Hidden", value="True/False. Hidden rooms will not display their entrance buttons to be travelled to from other rooms, and will remain so until their reveal parameters are met.")
    embed.add_field(name="Locked", value="True/False. Locked rooms will have their alt_entrance displayed and be unselectable unless their unlock parameters are met.")
    embed.add_field(name="End", value="True/False. If marked true, this room will end the adventure. Once ended, the adventure will no longer be playable unless the adventure epilogue is true. If the ending involves the player dying, the deathnote will be displayed to all players. Players reaching an ending room will count towards the adevnture total plays.")
    embed.add_field(name="Once", value="True/False. If true, this room can only be entered once. The player may recieve the option to enter the room more than once, but if they player selects this room then the option will not appear again.")
    embed.add_field(name="Keys", value="A list of the keys which are given to the player upon entering the room. Keys have properties which may prevent themselves from being given to the player. Type the ID of the key then a space and then the amount of that key to be given. Separate by commas.\nExample:\n`keyid1 2, keyid2 3`\nThis will attempt to give two keyid1's to the player and 3 of keyid2.\ntry /architect keys for more information.")
    embed.add_field(name="Destroy", value="Similar but opposite to keys. List of keys which are destroyed when the player enters the room. If the player does not have the keys, nothing happens. Each time the player enters the room, that ammount of those keys will be destroyed. Separate by commas.\nExample:\n`keyid1 2, keyid2 3`\nThis will attempt to destroy two keyid1's in the player's inventory and 3 of keyid2.")
    embed.add_field(name="Exits", value="A list of rooms which can be accessed from this room. Each exit is a room ID. Rooms listed as exits here will display their entrance text as buttons at the bottom of this room. Separate by commas. Maximum 4 exits.\nExample:\n`roomid1, roomid2`")
    embed.add_field(name="Unlock", value="Logical expression. The keys the player has will be fed into the expression. If the expression is true, the room will be unlocked. If the room is not locked, this will do nothing. The expression should contain key IDs using operators. Try `/architect operators` for more. ")
    embed.add_field(name="Reveal", value="Logical expression. The keys the player has will be fed into the expression. If the expression is true, the room will be revealed. If the room is not hidden, this will do nothing. The expression should contain key IDs using operators. Try `/architect operators` for more.")
    embed.add_field(name="Hide", value="Logical expression. The keys the player has will be fed into the expression. If the expression is true, the room will be hidden. If the room is not locked, this will do nothing. The expression should contain key IDs using operators. Try `/architect operators` for more.")
    embed.add_field(name="Lock", value="Logical expression. The keys the player has will be fed into the expression. If the expression is true, the room will be locked. If the room is not locked, this will do nothing. The expression should contain key IDs using operators. Try `/architect operators` for more.")
  elif topic == "keys":
  #for key information
    embed = discord.Embed(title="Keys Additional Info", description="Keys are ways to track how players are progressing through the adventure. The adventure does not change, nor do the rooms change. The keys the player has change, which may change which rooms are available to the player. Keys need not be literal keys which unlock rooms, but can be conecpts like the favor of an NPC. Keys can optionally be shown to the player, in their journal or inventory or both.")
    embed.add_field(name="Creating a Key", value="Use /newkey to start writing a new key. You can /editkey that key later. You do not need to specify anything to create a key, and all fields you don't specify will default to empty or False.")
    embed.add_field(name="Key ID", value="This is the unique ID of the key. It is used to reference the key in commands. You can specify an ID for the key or leave this blank and a random ID will be generated. IDs cannot be duplicated across any key that any player has put in any adventure.")
    embed.add_field(name="Display Name", value="This is the title of the key as displayed to players. This will only be displayed if the key has Journal or Inventory set to true. Display names do not need to be unique.")
    embed.add_field(name="Inventory", value="True/False. If true, this key will be displayed in the player's inventory. If false, this key will not be displayed in the player's inventory. Inventory items are physical things the player has aquired during the adventure. Keys can be both inventory items and journal entries.")
    embed.add_field(name="Journal", value="True/False. If true, this key will be displayed in the player's journal. When displayed, the text written in the key's Note field will be displayed. This can be used to make journal entries for major events in the adventure. Keys can have journal entries while still being physical items. Keys which have no inventory or journal will never be displayed to the player, but can still be used to track player progress.")
    embed.add_field(name="Description", value="This will only be displayed if the key has Inventory set to true. This is for physical descriptions of the object that the player has aquired in their inventory. This is also a good place to put hints about what the key does, or where it can be used. Usually written in second person.")
    embed.add_field(name="Note", value="This is the text that will be displayed to the player when they view their journal. Will only be displayed if the key has Journal set to true. Usually written in second person. You can use alt_note to display a new journal entry when the key leaves the player.")
    embed.add_field(name="Alt_Note", value="This is the text that will be displayed to the player when they view their journal, but only when the key is removed from the player. The removal of the key will generate a new journal entry, with this text. You can use this to update the player on the story.")
    embed.add_field(name="Subkeys", value="A list of key IDs and number that this key breaks into when the player deconstructs the key. This will create new keys in the player's inventory, and destroy the original key. Players can also combine keys together, if they have all the subkeys. Separate by commas.\nExample: `subkey 2, othersubkey 3`\nThis means the key's subkeys are two of the key subkey and three of the key othersubkey.")
    embed.add_field(name="Combine", value="True/False. If true, this key can be combined with other keys to create a new key. Players can attempt to combine keys which are combinable, but are not given hints as to what keys combine with what unless you give them a hint in the key's description or note.")
    embed.add_field(name="Deconstruct", value="True/False. If true, this key can be deconstructed. This deconstruction will yield the subkeys of the key, and may not work in reverse if any of the subkeys are not constructable.")
    embed.add_field(name="Unique", value="True/False. If true, this key can only be given once. When the player recieves this key, they will not be able to recieve it again by a room. The player may still be able to construct this key from its subkeys.")
    embed.add_field(name="Repeating", value="True/False. If true, this key will be given to the player every time they enter the room. If false, the presence of this key will prevent rooms from giving the player more of this same key.")
    embed.add_field(name="Stackable", value="True/False. If true, the player may have more than one of this key. If false, the player will not be able to aquire more than one from a room. The player will still be able to combine subkeys together to make this key.")
  elif topic == "journal":
  #for journal information
    embed = discord.Embed(title="Journal Additional Info", description="Journal entries are ways to track how players are progressing through the adventure. Players always track key information as they gain/lose keys in an adventure, but they don't always get to read about that information.")
    embed.add_field(name="Journal Entries", value="If a key has journal set to true, the information in the note field will be displayed as a journal entry. The entry is added to the player's journal when the key is given to them, and does not disappear when the key is removed. Keys will normally only generate a journal entry once (see below). This can be used to track major events in the adventure.")
    embed.add_field(name="Removed Journal Entries", value="If a key has an alt_note set, the alt_note will be displayed as a new journal entry when the key is removed. This is the only way for one key to generate more than one journal entry. Alternatively, a new key with a new note can be given to achieve a similar effect.")
  elif topic == "inventory":
  #for inventory information
    embed = discord.Embed(title="Inventory Additional Info", description="Inventory items are physical things the player has aquired during the adventure. Keys can be both inventory items and journal entries, or neither.")
    embed.add_field(name="Inventory Items", value="If a key has inventory set to true, the key will be given to the player if the player meets the requirements for the key. See /architect keys for more information. Players will be shown an inventory button only if/when they recieve a key with inventory set to true. The button will display the key's displayname, and the description if the key will be given in the inventory screen.")
    embed.add_field(name="Inventory Combinations", value="Some keys can be combined together, or deconstructed into other keys. See /architect keys for more information. Players are given the option to try and combine keys together if any keys in their inventory are combinable. If they are successful, they will recieve the new key. If they are unsuccessful, they will be given an incorrect combination message.")
    embed.add_field(name="Inventory Memory", value="Despite no longer being shown to the player, the player's data remembers which keys they have recieved in the past. Removing a key from a player's inventory won't remove it from their journal if that key has a journal entry.")
  elif topic == "expressions":
    conditions_examples = [
  "- `key2 and key4 and key5`\n(true if player has at least one of each)",
  "- `not key3`\n(true if the player has no key3)",
  "- `key1 = (key1 + key3)`\n(true if amount of key1 is equal to the sum of the amounts of key1 and key3)",
  "- `key1 = 3 and not (key2 > key3)`\n(will be true if key1 is 3 and also only if key2 is not greater than key3)",
  "- `key1 > 10 and key1 < 20`\n(true if the amount of key1 is between 10 and 20, noninclusive)",
  "- `((key1 - key2) + (key3 - key4)) > 5`\n(you'll need to use PEMDAS for this one)",
  "- `key4 > 4, key5 = 2, key6 + 3 = 5`\n(the commas here split this into three expressions, all of which must be true)"
]
  #for expressions information
    embed = discord.Embed(title="Expressions", description="Expressions are logical statements about keys. An expression being evaluated is known as returning. Expressions can either return as true or false. Expressions are exclusively used in these four Room fields: `lock`, `unlock`, `hide`, and `reveal`. The keys the player currently has are checked against the expression. If the expression returns true, then one of those four things happens to the room. You can separate expressions by commas or group them together with operators.")
    embed.add_field(name="Comparative Operators", value="Operators are symbols used to decide if an expression is true or false. Some operators can be used to compare: `and`, `or`, `not`, `=`, `!=`, `>`, `<`, `>=`, `<=`\nYou can optionally separate expressions with commas, or group them together with different operators.", inline=False)
    embed.add_field(name="Mathematic Operators", value="Operators can also be used to do math. These perform an arithmatic operation within the expression. The numbers of keys can be used together regardless of the type of key. You can add `+`, subtract `-`, multiply `*` and divide `/`\nAll math is completed before comparative operations.", inline=False)
    embed.add_field(name="and", value="The `and` operator will return true if both expressions on both sides are true. You can use `and` to bridge multiple expressions together. For example; `key1 > 1 and key2 > 1` will return true if both keys are greater than 1.")
    embed.add_field(name="or", value="The `or` operator will return true if either expression on either side is true. You can use `or` to bridge multiple expressions together. For example; `key1 > 1 or key2 > 1` will return true if either key is greater than 1.")
    embed.add_field(name="not", value="The `not` operator will return true if the expression on the right is false. Not recommended unless you know your logic tables pretty well. For example, `key1 and not key3 = 2` will return true if player has and key1 AND key3 isn't 2.")
    embed.add_field(name="=", value="The `=` operator will return true if the two expressions are equal. You can use `=` to bridge multiple expressions together. For example; `key1 = key2 + 1` will return true if key1 is equal to key2 plus one.")
    embed.add_field(name="!=", value="The `!=` means NOT EQUAL. This will return true if the two expressions are unequal. This works like the opposite of `=`. You can also use `!=` to bridge multiple expressions together. For example; `key1 != key3` will return true if key 1 is not equal to key 3.")
    embed.add_field(name=">", value="The `>` operator will return true if the left expression is greater than the right expression. You can use `>` to bridge multiple expressions together. For example; `key1 + 3 > key2` will return true if key1 plus three is greater than key2.")
    embed.add_field(name="<", value="The `<` operator will return true if the first expression is less than the second expression. You can use `<` to bridge multiple expressions together. For example; `key1 < 3 + key2 will return true if key1 is less than key2 plus 3.")
    embed.add_field(name=">=", value="The `>=` operator means greater than OR equal to. It will return true if the first expression is greater than or equal to the second expression. You can use `>=` to bridge multiple expressions together. For example; `key1 >= key2` will return true if key1 is greater than or equal to key2.")
    embed.add_field(name="<=", value="The `<=` operator means less than OR equal to. It will return true if the first expression is less than or equal to the second expression. You can use `<=` to bridge multiple expressions together. For example; `key1 <= key2` will return true if key1 is less than or equal to key2.")
    embed.add_field(name="Parenthesis", value="Besides using commas, you can group expressions together with parentheses to form large and complex expressions. For example, `(key1 + key2) = (key3 + key4)` will return true if key1 and key2 add up to the same amount as key3 and key4 added together. You can nest parentheses, but be cautioned against overly complex expressions.", inline=False)
    embed.add_field(name="Missing Keys", value="If a player does not have one of the keys in the expression, that key will be treated as a zero. You can test for this with things like `key1 = 0 and not key2 = 0` which will return true if the player doesn't have key1 and has at least 1 key2. You can also add keys together that the player doesn't have, like `key1 + key2 > 3` would add 0 + 0 unless the player has those keys. If they have four of just one of those keys, it would return true.", inline=False)
    embed.add_field(name="Lone Expressions", value="You can also input keys on their own as an expression. For example; `key2` by itself will return true if the player has any of key2. Using operators with solo keys might return unintuitive results. For example, if you use `key1 > key2 and key3` will return true if key1 is greater than key2 AND a player has at least one key3. It does not check if key1 is greater than both key2 and key3, for that you would need `key1 > key2, key1 > key3`", inline=False)
    embed.add_field(name="Grouped Expressions", value="When entering expressions, you can enter multiple at once by separating them by commas. They will appear as bullet points in your room confirmation preview. You can think of commas like AND. For example; `key1 > 3, key2 > 3` is the same as `key1 > 3 and key2 > 3`", inline=False)
    conditions_examples = "\n".join(conditions_examples)
    embed.add_field(name="Examples", value=f"These are some examples of valid expressions you can input into your rooms. Substitute these keys names for your key IDs\n{conditions_examples}", inline=False)
  #incorrect topic used
  else:
    embed = discord.Embed(title="Unknown topic", description=f"The topic {topic} was not recognized. Try /architect and leave the options blank for a list of all the topics you can use with the architect command. If you are having issues, please contact Ironically-Tall.")


  await ctx.reply(embed=embed, ephemeral=True)

@architecthelp.autocomplete("topic")
async def autocomplete_help(interaction: discord.Interaction, current: str):
  all_commands = ["Adventures", "Rooms", "Keys", "Journal", "Inventory", "Expressions"]
  choices = []
  for cmd in all_commands:
    if current.lower() in cmd.lower():
      choices.append(app_commands.Choice(name=cmd, value=cmd))
  return choices

async def setup(bot):
  bot.add_command(architecthelp)