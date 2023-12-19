import os
from collections import Counter

import discord
from discord import app_commands
from discord.ext import commands

import database
import formatter
from adventure import Adventure
from database import RoomButton
from player import Player

#token for use with discord API
my_secret = os.environ['TOKEN']

#intents rescricts scope of discord bot
intents = discord.Intents().all()

protectedchannels = [
  770017224844116031,
  1180274480807956631,
  1180315816294625291,
  1186398826148417707,
  1186464529366921286
]

#bot will be the async client for running commands
#remove help to replace with my own
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
guild_ids = [730468423586414624]

#simple ping command for testing
@bot.slash_command(name='ping', description='Ping the bot', guild_ids=guild_ids)
async def ping(ctx):
  await ctx.send('Pong!\n {0}'.format(round(bot.latency, 1)) + " seconds")
  
def player_alive(name):
  player = database.get_player(name)
  if player:
    return player["alive"]
  else:
    return None
  
def player_architect(roles):
  role_names = []
  for role in roles:
    role_names.append(role.name)
  return 'architect' in role_names

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
      embed.add_field(name=adventure["name"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  adventure = database.get_adventure(adventure_name.lower())
  if not adventure:
    embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please !join one of these adventures to begin:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["name"].title(), value=adventure["description"], inline=False)
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

@bot.command()
async def buttontest(ctx):
  view = discord.ui.View()
  view.add_item(RoomButton("Button 1", "test"))
  await ctx.reply("Button Test", view=view)

@bot.command()
async def newroom(ctx):
  truename = ctx.author.id
  name = ctx.author.display_name
  try:
    database.create_blank_room(truename)
    embed = formatter.blank_embed(name, "Success", "Room was created", "green")
  except Exception as e:
    embed = formatter.blank_embed(name, "Error", str(e), "red")
  await ctx.reply(embed=embed)

@bot.command()
async def newitem(ctx):
  name = ctx.author.display_name
  try:
    database.create_blank_item()
    embed = formatter.blank_embed(name, "Success", "Item was created", "green")
  except Exception as e:
    embed = formatter.blank_embed(name, "Error", str(e), "red")
  await ctx.reply(embed=embed)

@bot.command()
async def blankadventure(ctx):
  truename = ctx.author.id
  name = ctx.author.display_name
  try:
    database.create_blank_adventure(truename)
    embed = formatter.blank_embed(name, "Success", "Adventure was created", "green")
  except Exception as e:
    embed = formatter.blank_embed(name, "Error", str(e), "red")
  await ctx.reply(embed=embed)

#removes players from the database
@bot.command()
async def leave(ctx):
  truename = ctx.author.id
  name = ctx.author.display_name
  player = database.get_player(truename)
  if player:
    channel = bot.get_channel(player["channel"])
    tuple = await database.confirm_embed("Leaving the game will delete all of your data and delete this thread. Click *Yes* to continue or *No* to cancel:", "leave" , channel)
    embed = tuple[0]
    view = tuple[1]
  else:
    embed = formatter.embed_message(name, "Error", "notplayer" , "red")
    view = discord.ui.View()
  await ctx.send(embed=embed, view=view)
  await ctx.message.delete()

@bot.command()
async def roomtree(ctx, *args):
  adventure_name = []
  truename = ctx.author.id
  name = ctx.author.display_name
  all_rooms = database.get_all_rooms()
  for arg in args:
    adventure_name.append(str(arg))
  adventure_name = " ".join(adventure_name)
  adventure = database.get_adventure(adventure_name)
  if adventure:
    test_adventure = Adventure(name=adventure["name"], author=adventure["author"], description=adventure["description"], start=adventure["start"])
    test_adventure.build_room_tree(adventure["start"])
    print(test_adventure.room_tree)
    tree = "\n".join(test_adventure.tree)
    await ctx.reply("```" + tree + "```")
  else:
    return
  
  
#allows admin to add new architects
@bot.command()
async def architect(ctx, disc=None):
  roles = ctx.author.roles
  name = ctx.author.display_name
  truename = ctx.author.id
  if disc is None:
    embed = formatter.embed_message(name, "Error", "needuser", "red")
    await ctx.reply(embed=embed)
    return
  else:
    id = disc[2:-1] if disc else 'ERROR'
    arch_true = database.get_player_info(id, "architect")
  if not player_architect(roles):
    embed = formatter.embed_message(name, "Error", "notarchitect", "red")
  elif arch_true:
    embed = formatter.embed_message(name, "Error", "alreadyarchitect", "red")
  else:
    dict = {"disc": truename,"architect": True}
    database.update_player(dict)
    embed = formatter.embed_message(name, "Success", "newarchitect", "green")
  await ctx.reply(embed=embed)
  
#resets a player back to the start, ressurects them
@bot.command()
async def newgame(ctx, *args):
  truename = ctx.author.id
  name = ctx.author.display_name
  if database.get_player(truename):
    player_update = {"disc": truename, "alive": True, "room": "kitchen", "inventory": [], "taken": []}
    database.update_player(player_update)
    embed = formatter.embed_message(name, "New Game", "newgame", "green")
  else:
    embed = formatter.embed_message(name, "Error", "notplayer", "red")
  await ctx.reply(embed=embed)
  
#replies with the description of the current room to the player
@bot.command()
async def info(ctx):
  truename = ctx.author.id
  player = database.get_player(truename)
  if player:
    room_name = player["room"]
    all_items = player["inventory"]
    new_items = []
    room = database.get_room(room_name)
  else:
    print("ERROR - PLAYER DATA NOT FOUND")
    return
  if room:
    tuple = database.embed_room(all_items, new_items, room["displayname"], room)
  else:
    return
  embed = tuple[0]
  view = tuple[1]
  await ctx.reply(embed=embed, view=view)

#takes the path chosen by the player into the next room
#if the player is dead, rejects message
@bot.command()
async def path(ctx, exit):
  truename = ctx.author.id
  name = ctx.author.display_name
  try:
    trueexit = int(exit) - 1 #makes sure the exit is valid int
  except Exception as e:
    embed = formatter.embed_message(name, "Error", "exitformat", "red")
    print(e)
    await ctx.reply(embed=embed)
    return
  room = database.get_player_room(truename) #current room
  all_items = database.get_player_info(truename, "inventory")
  taken = database.get_player_info(truename, "taken")
  if taken is None:
    taken = []
  if room is None: #should not fire unless player is broken
    print("Error - Room is None!")
    embed = formatter.embed_message(name, "Error", "noroom", "red")
    await ctx.reply(embed=embed)
    return
  #if player exists and is alive
  if database.get_player(truename) and player_alive(truename) and room:
    #is the exit is valid
    if database.check_valid_exit(truename, trueexit):
      newroomname = room["exit_destination"][trueexit]
      newroom = database.get_room(newroomname)
      new_items = []
      #if the room has an item in it
      if newroom and newroom["items"]:
        items_list = give_player_items(newroom, all_items, taken)
        new_items = items_list[0]
        all_items = items_list[1]
      dict = {"disc": truename,"room": newroomname, "inventory": all_items, "taken": taken}
      database.update_player(dict)
      tuple = formatter.embed_room(all_items, new_items, "You enter the " + newroomname, newroom, "purple")
      embed = tuple[0]
      view = tuple[1]
    else:
      embed = formatter.embed_message(name, "Path Blocked", "exitblocked", "red")
      await ctx.reply(embed=embed)
      return
  else:
    print("Error - Player is dead or not in a room!")
    embed = formatter.embed_message(name, "Error", "exitformat", "red")
    await ctx.reply(embed=embed)
    return
  await ctx.reply(embed=embed, view = view)
  
#allows player to kill themselves... for testing purposes
@bot.command()
async def kill(ctx):
  truename = ctx.author.id
  dict = {"disc": truename,"alive": False}
  database.update_player(dict)
  await ctx.reply(ctx.author.mention + " you died!")

#returns a list of the truenames of items for the player
@bot.command()
async def inventory(ctx):
  truename = ctx.author.id
  real_items = database.get_player_info(truename, "inventory")
  embed = formatter.inventory(real_items)
  await ctx.reply(embed=embed)

#attempts to combine two items or more together
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
        inventory.append(item["name"])
        dict = {"disc": truename,"inventory": inventory}
        database.update_player(dict)
        embed = formatter.embed_message(name, "You created a " + item["displayname"] + "!", "combo", "green")
        await ctx.reply(embed=embed)
        return
  embed = formatter.embed_message(name, "Incorrect Combination", "nocombo", "red")
  await ctx.reply(embed=embed)
  return

#deconstructs an item, if such a thing is possible for that item
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
  
#allows any player to start a new adventure
#really only makes a new room, adding that room to adventures
@bot.command()
async def newadventure(ctx, adventure_name):
  roles = ctx.author.roles
  if not player_architect(roles):
    embed = formatter.embed_message(ctx.author.display_name, "Error", "notarchitect", "red")
    await ctx.reply(embed=embed)
    return
  name = ctx.author.display_name
  adventure_name = adventure_name.lower()
  adventures = database.get_adventures()
  adventure_names = []
  for adventure in adventures:
    adventure_names.append(adventure["name"])
  if adventure_name in adventure_names:
    embed = formatter.embed_message(name, "Error", "adventureexists", "red")
    await ctx.reply(embed=embed)
    return
  pass

@bot.command()
async def adventures(ctx):
  guild = ctx.guild
  adventures = database.get_adventures()
  adventure_names = []
  descriptions = []
  authors = []
  for adventure in adventures:
    adventure_names.append(adventure["name"])
    descriptions.append(adventure["description"])
    author = guild.get_member(adventure["author"])
    authors.append(author.display_name)
  embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use !join <name of the adventure> to start playing. More adventures will be available later!", color=0x00ff00)
  for i in range(len(adventure_names)):
    embed.add_field(name=adventure_names[i].title(), value=descriptions[i] + "\nCreated by: " + authors[i], inline=False)
  await ctx.reply(embed=embed)
  return
  
#basic help command, replies with embed
#allows the user to optionally !help other commands
@bot.command()
async def help(ctx, *args):
  message = args[0] if len(args) > 0 else ""
  await ctx.reply(embed=formatter.help(message))


#prints a connection message to the console for debugging
@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')

#prevents bot from answering its own messages
#requires messages stay in specific channels
#ignores messages that arent commands
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if not message.content.startswith("!"):
    return
  if message.channel.id in protectedchannels:
    await bot.process_commands(message)
  else:
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
