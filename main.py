import os  #used to store secrets
from collections import Counter  #list comparing tool

import discord  #all bot functionality
from discord.ext import commands  #commands for bot

import database  #mongodb database
import formatter  #formats embeds
from player import Player  #player class
from room import Room  #room class

#token for use with discord API
my_secret = os.environ['TOKEN']

#intents rescricts scope of discord bot
intents = discord.Intents().all()

#the channel ID needs to be in this list
#bot ignores all other channels
protectedchannels = [
  770017224844116031,
  1180274480807956631,
  1180315816294625291,
  1186398826148417707,
  1186464529366921286,
  908522799772102739,
  1183954110513414164,
  1187417491576729620,

]
#bot will be the async client for running commands
#remove help to replace with my own
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

#guild IDs that the bot is in, for now
guild_ids = [730468423586414624]

#simple ping command for testing
@bot.command()
async def ping(ctx):
  await ctx.reply('Pong!\n {0}'.format(round(bot.latency, 1)) + " seconds")

@bot.tree.command(name="register", description="Register a bot to a channel")
async def register(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    guild_id = interaction.guild_id
    if database.register_channel(channel_id, guild_id):
      await interaction.response.send_message("Bot has been registered to this channel.", ephemeral=True)
      print(f"Bot has been registered to channel: {channel_id}")
    else:
      await interaction.response.send_message("Failed to register the bot: guild already has a channel registered.", ephemeral=True)
      print("Error in register command: guild already has a channel in the database")

#generate unique ID and send for testing purposes
@bot.command()
async def randomid(ctx, *args):
  arg = int(''.join(args))
  await ctx.reply(database.generate_unique_id(arg))

@bot.command()
async def updaterooms(ctx):
  all_rooms = database.rooms.find()
  for room in all_rooms:
    room_object = Room(dict=room)
    room_id = room_object.roomid
    room_name = room_object.displayname
    print("checking room " + room_name)
    print("room ID: " + str(room_id))
    dict = room_object.__dict__
    database.update_room(dict)
    await ctx.send("room " + room_name + " updated with ID " + str(room_id) + " but still has a name")

#NUCLEAR DELETION OF ROOM FIELDS
#@bot.command()
#async def deleteroomfields(ctx, *args):
  #arg = ''.join(args)
  #database.delete_room_fields(arg)
  #await ctx.send(str(arg) + " removed from all rooms")

#old version, new version is handled by database
#injests items a room has, player inventory, player taken
#determines if the player needs to be given the item
#prevents duplicate items, returns a tuple
def give_player_items(new_items, old_items, taken):
  items_grouping = [new_items, old_items, taken]
  for item in new_items:
    item_object = None
    item_object = database.items.find_one({"name" : item})
    if not item_object:
      print("ERROR - Room item not found!")
      print(str(item) + " does not exist as an item name")
      continue
    elif item in old_items:
      new_items.remove(item)
      continue
    elif item in taken and not item_object["infinite"]:
      new_items.remove(item)
      continue
    elif item_object["infinite"] and item not in old_items:
      if item not in taken:
        taken.append(item)
      old_items.append(item)
    elif item not in old_items and item not in taken:
      taken.append(item)
      old_items.append(item)
    else:
      new_items.remove(item)
  database.pp("New Items:" + str(items_grouping))
  return items_grouping
  
#creates new players and adds them to the database
@bot.command()
async def join(ctx, *args):
  adventure_name = []
  truename = ctx.author.id
  name = ctx.author.display_name
  channel = ctx.channel
  if database.get_player(truename):
    embed = formatter.embed_message(name, "Error", "alreadyplayer" , "red")
    await ctx.reply(embed=embed)
    return
  for arg in args:
    adventure_name.append(str(arg))
  adventure_name = " ".join(adventure_name)
  all_adventures = database.get_adventures()
  if adventure_name == "":
    embed = discord.Embed(title="Error - Need adventure", description="You need to specify an adventure to join. Use !join <adventure name here>\nRefer to this list of available adventures:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  adventure = database.get_adventure(adventure_name.lower())
  if not adventure:
    embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please !join one of these adventures to begin:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  else:
    guild = ctx.guild
    thread = await channel.create_thread(name=name + "'s " + adventure_name)
    channel_id = thread.id
    player = Player(truename, name, adventure["start"], channel_id)
    database.new_player(player.__dict__)
    room = database.get_player_room(truename)
    if room is None:
      print("Error! Room is None!")
      embed = formatter.embed_message(name, "Error", "noroom", "red")
      await ctx.reply(embed=embed)
      return
    room_author = guild.get_member(room["author"])
    room_author_displayname = 'ERROR' if room_author is None else str(room_author.display_name)
    all_items = []
    new_items = []
    tuple = database.embed_room(all_items, new_items, room["displayname"], room)
    embed = tuple[0]
    view = tuple[1]
    embed.set_footer(text="This room was created by " + room_author_displayname)
    #un-comment to delete command after success
    #await ctx.message.delete()
    await thread.send(ctx.author.mention + "You have sucessfully begun an adventure. Use the buttons below to play. If you have questions, ask a moderator",embed=embed, view=view)

#creation mode for adding anything new or editing rooms
#edits one adventure at a time
#works similar to join, creates a private thread
@bot.command()
async def create(ctx, *args):
  adventure_name = []
  name = ctx.author.display_name
  channel = ctx.channel
  #delete comment to implememnt admin check
  #if player and not player["architect"]:
    #embed = formatter.embed_message(name, "Error", "notarchitect" , "red")
    #await ctx.reply(embed=embed)
    #return
  for arg in args:
    adventure_name.append(str(arg))
  adventure_name = " ".join(adventure_name)
  all_adventures = database.get_adventures()
  database.pp(all_adventures)
  if adventure_name == "":
    embed = discord.Embed(title="Error - Need adventure", description="You need to specify an adventure to begin creating. Use !create <adventure name here>\nRefer to this list of available adventures to edit:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  adventure = database.get_adventure(adventure_name.lower())
  if not adventure:
    embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please !create one of these adventures to begin creation mode:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  else:
    thread = await channel.create_thread(name=name + " editing " + adventure_name)
    channel = bot.get_channel(thread.id)
    tuple = await database.creation_mode(channel)
    embed = tuple[0]
    view = tuple[1]
    await ctx.message.delete()
    await thread.send(ctx.author.mention + "This is create mode",embed=embed, view=view)

#attempts to combine two items or more together
#soon to be removed, in favor of embed function
@bot.command()
async def combine(ctx, *args):
  truename = ctx.author.id
  inventory = database.get_player_info(truename, "inventory")
  name = ctx.author.display_name
  if len(args) < 2:
    embed = formatter.embed_message(name, "Error", "noitem", "red")
    await ctx.reply(embed=embed)
    return
  try:
    if inventory is None:
      embed = formatter.embed_message(name, "Error", "emptyinventory", "red")
      await ctx.reply(embed=embed)
      return
    for arg in args:
      if int(arg) > len(inventory):
        embed = formatter.embed_message(name, "Error", "noitem", "red")
        await ctx.reply(embed=embed)
        return
  except Exception as e:
    print(e)
    embed = formatter.embed_message(name, "Error", "noitem", "red")
    await ctx.reply(embed=embed)
    return
  combining_items = []
  for arg in args:
    combining_items.append(inventory[int(arg)-1])
  all_items = database.get_all_items()
  for item in all_items:
    if item["subitems"]:
      print("combining items...")
      print(item["subitems"])
      print(combining_items)
      if Counter(combining_items) == Counter(item["subitems"]):
        for olditem in combining_items:
          inventory.remove(olditem)
        inventory.append(item["itemid"])
        dict = {"disc": truename,"inventory": inventory}
        database.update_player(dict)
        embed = formatter.embed_message(name, "You created a " + item["displayname"] + "!", "combo", "green")
        await ctx.reply(embed=embed)
        return
  embed = formatter.embed_message(name, "Incorrect Combination", "nocombo", "red")
  await ctx.reply(embed=embed)
  return

#deconstructs an item, if such a thing is possible for that item
#soon to be removed, in favor of embed function
@bot.command()
async def deconstruct(ctx, item):
  truename = ctx.author.id
  inventory = database.get_player_info(truename, "inventory")
  name = ctx.author.display_name
  if inventory is None:
    embed = formatter.embed_message(name, "Error", "emptyinventory", "red")
    await ctx.reply(embed=embed)
    return
  try:
    trueitem = int(item)
    trueitem -= 1
    if int(item) > len(inventory):
      embed = formatter.embed_message(name, "Error", "noitem", "red")
      await ctx.reply(embed=embed)
      return
  except Exception as e:
    print(e)
    embed = formatter.embed_message(name, "Error", "noitem", "red")
    await ctx.reply(embed=embed)
    return
  scrap_item = inventory[trueitem]
  scrap_item = database.get_item(scrap_item)
  if scrap_item is None:
    embed = formatter.embed_message(name, "Error", "itemdoesntexist", "red")
    await ctx.reply(embed=embed)
    return
  new_items = scrap_item["subitems"]
  inventory.remove(scrap_item["name"])
  items_string = ""
  for item in new_items:
    inventory.append(item)
    itemname = database.get_item(item)
    if itemname:
      items_string = items_string + ("- " +itemname["displayname"] + "\n")
  dict = {"disc": truename,"inventory": inventory}
  database.update_player(dict)
  embed = formatter.blank_embed(name, "You deconstruct the " + scrap_item["displayname"], "after deconstruction the following items are added to your inventory:\n" + items_string, "green")
  await ctx.reply(embed=embed)
  return

#basic help command, replies with embed
#allows the user to optionally !help other commands
@bot.command()
async def help(ctx, *args):
  message = args[0] if len(args) > 0 else ""
  await ctx.reply(embed=formatter.help(message))

#Slash commands start here!!!!
#Slash commands start here!!!!
#Slash commands start here!!!!
#Slash commands start here!!!!
#Slash commands start here!!!!

#Makes a new room in the database
@bot.tree.command(name= "newroom", description= "Create a new room")
async def newroom(interaction: discord.Interaction):
    truename = interaction.user.id
    name = interaction.user.display_name  # Define the 'name' variable within the 'newroom' command
    try:
        database.create_blank_room(truename)
        embed = formatter.blank_embed(name, "Success", "Room was created, use the get room command /getroom  to view the room you just made.", "green")
    except Exception as e:
        embed = formatter.blank_embed(name, "Error", str(e), "red")
    await interaction.response.send_message(embed=embed)

#Makes a new blank item in the database
@bot.tree.command(name= "newitem", description= "Create a new item")
async def newitem(interaction: discord.Interaction):
      author_id = interaction.user.id  # capture the user ID of the person interacting
      name = interaction.user.display_name
      try:
        database.create_blank_item(author_id)  # pass the user ID to create_blank_item
        embed = formatter.blank_embed(name, "Success", "Item was created", "green")
      except Exception as e:
        embed = formatter.blank_embed(name, "Error", str(e), "red")
      await interaction.response.send_message(embed=embed)

#makes a new adventure in the database
@bot.tree.command(name="newadventure", description="Create a new adventure")
async def newadventure(interaction: discord.Interaction):
    truename = interaction.user.id
    name = interaction.user.display_name
    channel = interaction.channel
    # Check if the author already has an adventure
    if database.testadventures.find_one({"author": truename}):
        embed = formatter.blank_embed(name, "Error", "You already have an existing adventure. You cannot create more than one.", "red")
        await interaction.response.send_message(embed=embed)
        return
    # Check for existing edit thread
    player_info = database.get_player(truename)
    if player_info and player_info["edit_thread_id"] != "":
        embed = formatter.blank_embed(name, "Error", "You already have an existing thread for editing adventures. Please use that for editing your adventure.", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    # Check for the player existing in the database
    elif not player_info:
        embed = formatter.blank_embed(name, "Error", "You are not a player. Please use /join Example Adventure to begin", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    # Checks for the player having joined the example adventure
    elif player_info["current_adventure"] != "example adventure":
        embed = formatter.blank_embed(name, "Error", "You are not in the Example Adventure. Please use /join Example Adventure to begin", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    else:
        # Create the adventure first
        database.create_blank_adventure(truename)
        # Then, create a new thread for editing this adventure
        database.pp("creating adventure edit channel:\n" + str(channel))
        if channel and channel.type == discord.ChannelType.text:
          thread = await channel.create_thread(name=f"{name} editing an adventure")
          await thread.send(interaction.user.mention + " is editing an adventure.")
          edit_thread_id = channel.id
        # Update the player's editthread field with the new thread ID
          database.update_player({'disc': truename, 'edit_thread_id': edit_thread_id})
          embed = formatter.blank_embed(name, "Success", f"Adventure was created and your edit thread is ready! Thread ID: {edit_thread_id}", "green")
          await interaction.response.send_message(embed=embed, ephemeral=True)

#Leaves current game
@bot.tree.command(name= "leave", description= "Use this command to leave the game! (You can only leave if you are the host of the game)")
async def leave(interaction: discord.Interaction):
    truename = interaction.user.id
    name = interaction.user.display_name 
    player = database.get_player(truename)
    if player:
      channel = bot.get_channel(player["channel"])
      tuple = await database.confirm_embed("Leaving the game will delete all of your data and delete this thread. Click *Yes* to continue or *No* to cancel:", "leave" , channel)
      embed = tuple[0]
      view = tuple[1]
    else:
      embed = formatter.embed_message(name, "Error", "notplayer" , "red")
      view = discord.ui.View()
    await interaction.response.send_message(embed=embed, view=view)

#replies with the description of the current room to the player
@bot.tree.command(name= "info", description= "Learn about the room you are in")
async def info(interaction: discord.Interaction):
  truename = interaction.user.id
  player = database.get_player(truename)
  if player:
    if player["alive"]:
        room_name = player["room"]
        all_items = player["inventory"]
        new_items = []
        room = database.get_room(room_name)
    else:
      await interaction.response.send_message("You are either dead or not in a adventure!")
      return
    if room:
      tuple = database.embed_room(all_items, new_items, room["displayname"], room)
    else:
      return
    embed = tuple[0]
    view = tuple[1]
    await interaction.response.send_message(embed=embed, view=view)

#allows player to kill themselves... for testing purposes
@bot.tree.command(name= "kill", description= "A way out of the game")
async def kill(interaction: discord.Interaction):
      truename = interaction.user.id
      dict = {"disc": truename,"alive": False}
      database.update_player(dict)
      await interaction.response.send_message("You Died! Game over")

#returns a list of the truenames of items for the player
@bot.tree.command(name= "inventory", description= "View your inventory")
async def inventory(interaction: discord.Interaction):
    truename = interaction.user.id
    real_items = database.get_player_info(truename, "inventory")
    player = database.get_player(truename)
    embed = formatter.inventory(real_items)
    if player and player["alive"]:
      await interaction.response.send_message(embed=embed)
    else :
      await interaction.response.send_message("You are either dead or not in a adventure!")

#cupid for giantessworld valentines event
@bot.tree.command(name= "cupid", description= "Use this to submit your valentines request")
async def cupid(interaction: discord.Interaction):
  truename = interaction.user.id
  tuple = await database.cupid_embed(truename)
  embed = tuple[0]
  view = tuple[1]
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
  

#Lists the current adventures from the database
@bot.tree.command(name= "adventures", description= "A list of all playable adventures")
async def adventures(interaction: discord.Interaction):
    guild = interaction.guild
    adventures = database.get_adventures()
    adventure_names = []
    descriptions = []
    authors = []
    if guild is None:
      return
    for adventure in adventures:
        adventure_names.append(adventure["nameid"])
        descriptions.append(adventure["description"])
        author_id = adventure["author"]
        print(f"Author ID: {author_id}")
        author = guild.get_member(author_id)
        if author:
            authors.append(author.display_name)
        else:
            authors.append("Unknown Author")
    embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use !newgame to start the test adventure. More adventures will be available later!", color=0x00ff00)
    for i in range(len(adventure_names)):
      embed.add_field(name=adventure_names[i].title(), value=descriptions[i] + "\nCreated by: " + authors[i], inline=False)
    await interaction.response.send_message(embed=embed)
    return

#prints a connection message to the console for debugging
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    #this syncs the bot slash commands
    try: 
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        print(e)

#prevents bot from answering its own messages
#requires messages stay in specific channels
#ignores messages that arent commands
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if not message.content.startswith("!"):
    return
  if message.content.contains("cupid"):
    if message.channel.id == 1192186126623064084:
      await bot.process_commands(message)
    else:
      return
  if message.channel.id in protectedchannels:
    await bot.process_commands(message)
  else:
    # makes sure that player can only respond to specific thread
    player_id = message.author.id
    player_channel_id = database.get_player_info(player_id, "channel")
    if message.channel.id != player_channel_id:
      return
    else:
      await bot.process_commands(message)
  

#runs the bot and throws generic errors
try:
  print("running")
  database.ping()
  bot.run(my_secret)
except Exception as e:
  print(e)
