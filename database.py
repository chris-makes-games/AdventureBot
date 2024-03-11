import os  #stores secrets
import pathlib
import random as rand  #random number generator
from pprint import pprint as pp  #pretty printing

import discord
from discord.components import TextInput  #discord api
import pymongo  #mongo db api

from adventure import Adventure  #adventure class
from item import Item  #item class
from room import Room  #room class
from key import Key

#sets the parent directory of the bot
BASE_DIR = pathlib.Path(__file__).parent
#this is the command folder directory
CMDS_DIR = BASE_DIR / "cmds"


#button class for allowing the player to traverse rooms
#button sends player to destination room when clicked
class RoomButton(discord.ui.Button):
  def __init__(self, label, destination, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.destination = destination
    self.disabled = disabled
    self.row = row
  async def callback(self, interaction: discord.Interaction):
      await move_player(interaction, self.destination)

class CreateAdventureModal(discord.ui.Modal):
  def __init__(self):
    super().__init__(title="Create New Adventure")
    self.name = discord.ui.TextInput(label="Adventure Name", style=discord.TextStyle.short, required=True)
    self.description = discord.ui.TextInput(label="Adventure Description", style=discord.TextStyle.paragraph, required=True, placeholder="Describe Your Adventure. Be sure to include any themes or content warnings, if applicable.")
    self.add_item(self.name)
    self.add_item(self.description)
    #removed items from form, for now
    #self.add_item(self.items)
  async def on_submit(self, interaction: discord.Interaction):
    user_displayname = interaction.user.display_name
    start_room = Room(displayname="Default Start Room")
    adventure = Adventure(name=self.name.value, description = self.description.value, start=start_room.id, author=user_displayname, rooms=[start_room.id])
    create_new_adventure(adventure.__dict__)
    create_new_room(start_room.__dict__)
    await interaction.response.send_message(f"Adventure created:\nName: {self.name}\nDescription:\n{self.description}", ephemeral=True)

class CreateRoomModal(discord.ui.Modal):
  def __init__(self):
    super().__init__(title="Create New Room")
    self.name = discord.ui.TextInput(label="Room Name", style=discord.TextStyle.short, required=True)
    self.description = discord.ui.TextInput(label="Room Description", style=discord.TextStyle.paragraph, required=True, placeholder="You have moved into a dark place. It is pitch black. You are likely to be eaten by a grue.")
    self.items = discord.ui.TextInput(label="Room Items", placeholder="enter item IDs, separated by commas: Fs53, 6gHj, t2WQ", required=False, style=discord.TextStyle.short)
    self.add_item(self.name)
    self.add_item(self.description)
    #removed items from form, for now
    #self.add_item(self.items)
  async def on_submit(self, interaction: discord.Interaction):
    user_displayname = interaction.user.display_name
    room = Room(displayname= self.name.value, description = self.description.value, items = self.items.value, author=user_displayname)
    create_new_room(room.__dict__)
    await interaction.response.send_message(f"Room created:\nRoom display name: {self.name}\n description:\n{self.description}\nItems:\n{self.items}", ephemeral=True)

class CreateItemModal(discord.ui.Modal):
  def __init__(self):
    super().__init__(title="Create New Item")
    self.name = discord.ui.TextInput(label="Item Name", style=discord.TextStyle.short, required=True)
    self.description = discord.ui.TextInput(label="Item Description", style=discord.TextStyle.paragraph, required=True, placeholder="Describe your item for when the player checks their inventory.")
    self.add_item(self.name)
    self.add_item(self.description)
  async def on_submit(self, interaction: discord.Interaction):
    user_displayname = interaction.user.display_name
    item = Item(displayname= self.name.value, description = self.description.value, author=user_displayname)
    create_new_item(item.__dict__)
    await interaction.response.send_message(f"Item created:\nItem display name: {self.name}\n description:\n{self.description}", ephemeral=True)

#generates an embed with fields for the room
#when clicked, the room making embed is sent to the channel
class CreateRoomButton(discord.ui.Button):
  def __init__(self, label, disabled=False, row=0, roomname="INVALID NAME", roomdesc="INVALID DESCRIPTION"):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
    self.roomname = roomname
    self.roomdesc = roomdesc
  #callback is for when the button is clicked
  async def callback(self, interaction: discord.Interaction):
    new_room = Room(displayname=self.roomname, description = self.roomdesc, author=interaction.user.display_name)
    create_new_room(new_room.__dict__)
    await interaction.response.send_message(f"Room created:\nRoom display name: {self.roomname},\n description:\n{self.roomdesc}", ephemeral=True)

class CreateItemButton(discord.ui.Button):
  def __init__(self, label, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
  #callback is for when the button is clicked
  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CreateItemModal())

class ExitButton(discord.ui.Button):
  def __init__(self, label, channel, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.channel = channel
    self.disabled = disabled
    self.row = row
  #callback is for when the button is clicked
  async def callback(self):
    await self.channel.delete()

#simple button class to confirm or cancel any action
#can be placed on any embed that requires a confirmation
#action is the name of the action to be taken
class ConfirmButton(discord.ui.Button):
  def __init__(self, label, confirm, action, channel="", id=None, disabled=False, row=0):
    super().__init__(label=label)
    self.id = id
    self.confirm = confirm
    self.action = action
    self.disabled = disabled
    self.row = row
    self.channel = channel
    if self.confirm:
      self.style = discord.ButtonStyle.success
      self.emoji = "✅"
    else:
      self.style = discord.ButtonStyle.danger
      self.emoji = "✖️"
  #callback is for when the button is clicked
  async def callback(self, interaction: discord.Interaction):
    await interaction.response.defer()
    
    #if they hit the red x it does nothing
    #embed that is asking the conform is deleted
    if self.action == "cancel":
      await interaction.delete_original_response()
    #player wants to leave an adventure
    elif self.action == "leave":
      await interaction.followup.send(f"This would have made a player leave an adventure, and delete channel {self.id} but it is not implemented yet.", ephemeral=True)
    elif self.action == "create_room":
      await interaction.followup.send("This would create a room but it isn't implememnted yet! Check database.ConfirmButton", ephemeral=True)
    elif self.action == "delete_item":
      await interaction.followup.send(f"This would delete item {self.id} but it's not implemented yet! Check database.ConfirmButton", ephemeral=True)
    elif self.action == "delete_room":
      await interaction.followup.send(f"This would delete room {self.id} but it's not implemented yet! Check database.ConfirmButton", ephemeral=True)
    elif self.action == "delete_adventure":
      await interaction.followup.send(f"This would delete adventure {self.id} but it's not implemented yet! Check database.ConfirmButton", ephemeral=True)
    elif self.action == "delete_player":
      await interaction.followup.send(f"This would delete player {self.id} but it's not implemented yet! Check database.ConfirmButton", ephemeral=True)
    else:
      await interaction.followup.send(f"ERROR: That button has no interaction yet!", ephemeral=True)
      return

#deactivated valentines function
class CupidModal(discord.ui.Modal):
  def __init__(self, title="Valentines Event Sign-up", *args):
    super().__init__(title=title)
    self.likes = discord.ui.TextInput(label="What short story would you like?", placeholder="remember that it should stay within 3k words", style=discord.TextStyle.long, required=True)
    self.limits = discord.ui.TextInput(label="What should your valentine stay away from?", placeholder="these topics will not be included in the story you recieve.", style=discord.TextStyle.long, required=True)
    self.willing = discord.ui.TextInput(label="What are you willing to write?", placeholder="please include any limits you may have.", style=discord.TextStyle.long, required=True)
    self.add_item(self.likes)
    self.add_item(self.limits)
    self.add_item(self.willing)
  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    dict = {"disc": interaction.user.id, "displayname" : interaction.user.display_name, "likes": self.likes.value, "limits": self.limits.value, "willing": self.willing.value}
    new_cupid(dict)
    await give_role(interaction, "Valentine")
    await interaction.followup.send(f"{interaction.user.mention} Your have signed up for the valentines event! Please wait until Jan 24th to recieve your secret valentine and begin writing.", ephemeral=True)

#deactivated valentines function
class CupidButton(discord.ui.Button):
  def __init__(self, label, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CupidModal())

db_name = os.environ['DB_NAME']
db_pass = os.environ['DB_PASS']
db_user = os.environ['DB_USER']
db_serv = os.environ['DB_SERVER']

mongo_client = pymongo.MongoClient("mongodb+srv://" + 
db_user + ":" + db_pass + "@" + db_name + db_serv)

#checks to make sure database is connected
def ping():
  try:
    mongo_client.admin.command('ping')
    print("You successfully connected to MongoDB!")
  except Exception as e:
    print(e)

#creates the databse object in mongo_client
database_name = os.environ['COLLECTION']
db = getattr(mongo_client, database_name) #turns string to attribute

#cursor objects hold document data
#function similar to dicts but are not dicts!!
rooms = db.rooms
users = db.users
items = db.items
keys = db.keys
adventures = db.adventures
ids = db.ids
botinfo = db.botinfo
cupid = db.cupid

#lists for generating a random ID
all_numbers = ["0️", "1️", "2️", "3️", "4️", "5" ,"6️", "7️", "8️", "9️"]
all_upper_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
all_lower_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

#registers the channel to restrict commands to that location
def register_channel(channel_id, guild_id):
  bot_info_dict = {
      "channel": channel_id,
      "guild": guild_id  
  }
  if botinfo.find_one({"guild": guild_id}):
    return False
  else:
    botinfo.insert_one(bot_info_dict)
    return True

#checks if a command is inactive in botinfo
def inactive_check(command):
  return botinfo.find_one({"inactive": command})

#adds a command to the inactive list
def deactivate_command(command):
  document = botinfo.find_one({"commands": "deactivated"})
  if document:
    document["inactive"].append(command)
    botinfo.update_one({"commands": "deactivated"}, {"$set": document})

#removes a command from the inactive list
def activate_command(command):
  document = botinfo.find_one({"commands": "deactivated"})
  if document:
    document["inactive"].remove(command)
    botinfo.update_one({"commands": "deactivated"}, {"$set": document})
                   
#returns a tuple to check permissions in botinfo
#tuple[0] is maintainer
#tuple[1] is assistant
def check_permissions(id):
  maintainer = bool(botinfo.find_one({"maintainers": id}))
  assistant = bool(botinfo.find_one({"assistants": id}))
  tuple = (maintainer, assistant)
  return tuple

#adds a new maintainer to botinfo
def add_maintainer(user_id):
  botinfo.update_one({"maintainers": user_id}, {"$set": {"maintainers": user_id}})

#adds a new assistant to botinfo
def add_assistant(user_id):
  botinfo.update_one({"assistants": user_id}, {"$set": {"assistants": user_id}})

#gets names of all commands in file
#returns list of strings
def get_all_commands():
  all_commands = []
  for cmd_file in CMDS_DIR.glob("*.py"):
    if cmd_file.name != "__init__.py":
      all_commands.append(cmd_file.name[:-3])
  return all_commands

#only returns commands regular players should see
#any new admin command needs to be added to this list
def get_player_commands():
  all_commands = []
  admin_commands = ["register", "load", "unload", "reload", "sync", "updaterooms", "ping", "activate", "deactivate", "newassistant", "newmaintainer"]
  for cmd_file in CMDS_DIR.glob("*.py"):
    if cmd_file.name != "__init__.py" and cmd_file.name[:-3] not in admin_commands:
      all_commands.append(cmd_file.name[:-3])
  return all_commands

#creates an ID that does not exist in the master ID document
#optionally allows you to generate more IDs at once
def generate_unique_id(multiple=1):
  multiples = []
  all_characters = all_numbers + all_upper_letters + all_lower_letters
  id = []
  while len(multiples) < multiple:
    while len(id) < 4:
      r = rand.choice(all_characters)
      banned = ids.find_one({"id": "BANNED"})
      id.append(r)
      if len(id) == 4 and ids.find_one({"id": id}):
        print("wow, one in ~14 million chance of a duplicate id!")
        print(id)
        id = []
      elif len(id) == 4 and id in banned["words"]:
        print("wow, one in ~14 million chance of a swear word being generated as an ID")
        print(id)
        id = []
    multiples.append("".join(id))
    id = []
  return ", ".join(multiples)

#injests items a room has, player inventory, player taken
#determines if the player needs to be given the item
#prevents duplicate items, returns a tuple
def give_player_items(new_items, old_items, taken):
  items_grouping = [new_items, old_items, taken]
  for item in new_items:
    item_object = None
    item_object = items.find_one({"itemid" : item})
    if not item_object:
      print("ERROR - Room item not found!")
      print(str(item) + " does not exist as an item name")
      continue
    elif item in taken and not item_object["infinite"] or item in old_items:
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
  pp("New Items:" + str(items_grouping))
  return items_grouping

#gives player key in room if applicable
def process_player_keys(found_keys, current_keys, history):
  new_keys = []
  new_history = []
  for key_id in found_keys:
    key = keys.find_one({"id": key_id})
    if key["id"] in current_keys and key["stackable"]:
      new_keys.append(key["id"])
    if key["id"] not in current_keys or key["repeating"]:
      if key["unique"] and key["id"] in history:
        continue
      new_keys.append(key["id"])
      if key["unique"]:
        new_history.append(key["id"])
  return new_keys, new_history
    

#moves player to a new room
#sends an embed with the new room's description and buttons
async def move_player(interaction, destination):
  player = get_player(interaction.user.id)
  new_room = get_room(destination)
  new_items = []
  if player and new_room:
    inventory = player["inventory"]
    taken = player["taken"]
    print("inventory: " + str(inventory))
    print("taken: " + str(taken))
    newroomname = new_room["id"]
    newroomauthor = new_room["author"]
    guild = interaction.guild
    author = guild.get_member(newroomauthor)
    if not author:
      author = "Unknown"
  else:
    print("ERROR - None Object during database.moveplayer()")
    print("player: " + str(player))
    print("room: " + str(new_room))
    return
  if new_room["items"]:
    pp("items found!" + str(new_room["items"]))
    items_list = give_player_items(new_room["items"], inventory, taken)
    pp(items_list)
    new_items = items_list[0]
    inventory = items_list[1]
    taken = items_list[2]
  dict = {"disc": player["disc"],"room": newroomname, "inventory": inventory, "taken": taken}
  update_player(dict)
  tuple = embed_room(inventory, new_items, "You enter the " + newroomname, new_room, author)
  embed = tuple[0]
  view = tuple[1]
  await interaction.response.edit_message(embed=embed, view=view)

#sends an embed with room information and buttons for player to traverse
#returns a tuple of embed and view
def embed_room(all_items, new_items, title, room, author, color=0):
  if color == "":
    color = discord.Color.blue()
  descr = room["description"]
  embed = discord.Embed(title=title, description=descr, color=color)
  embed.set_footer(text="This room was created by " + author)
  if "url" in room:
    embed.set_image(url=room["url"])
  elif "URL" in room:
    embed.set_image(url=room["URL"])
  view = discord.ui.View()
  if new_items:
    for item in new_items:
      found_item = get_item(item)
      description = found_item["description"] if found_item else "ERROR - ITEM HAS NO NAME"
      embed.add_field(name="You found an item:", value=description, inline=False)
  if len(room["exits"]) == 0:
    embed.add_field(name="Exits", value="There are no exits from this room. This is the end of the line. Unless this room is broken?", inline=False)
  if len(room["exits"]) == 1:
    embed.add_field(
  name="This area has only one way out.",value="press the button below when you're ready", inline=False)
  else:
    embed.add_field(name="Choose a Path", value="Make your choice by clicking a button below:", inline=False)
  r = 1
  for exit in room["exits"]:
    if room["secrets"][r - 1] == "Open":
      button = RoomButton(label=str(exit), destination=room['exit_destination'][r - 1], row = r - 1)
      view.add_item(button)
    elif room["secrets"][r - 1] == "Secret":
      if room["unlockers"][r - 1] in all_items:
        button = RoomButton(label=str(exit), destination=room['exit_destination'][r - 1], row = r - 1)
        view.add_item(button)
    elif room["unlockers"][r - 1] in all_items:
      button = RoomButton(label=str(exit), destination=room['exit_destination'][r - 1], row = r - 1)
      view.add_item(button)
    else:
      button = RoomButton(label=room["secrets"][r - 1], destination=room['exit_destination'][r - 1], disabled=True, row = r - 1)
      view.add_item(button)
    r += 1
  return (embed, view)

#generic confirmation embed for when an action requires confirmation
#adds a ConfirmButton to itself at the bottom
#action is the action that the button will do
async def confirm_embed(confirm_text, action, channel, title="Are you Sure?", id=None):
  embed = discord.Embed(title=title, description=confirm_text, color=discord.Color.orange())
  confirm_button = ConfirmButton(label="Yes", confirm=True, action=action, channel=channel, id=id)
  deny_button = ConfirmButton(label="No", confirm=False, action="cancel", channel=channel)
  view = discord.ui.View()
  view.add_item(confirm_button)
  view.add_item(deny_button)
  if action == "leave":
    embed.set_image(url="https://i.kym-cdn.com/entries/icons/mobile/000/028/033/Screenshot_7.jpg")
  return (embed, view)

#WIP for creation mode
#this embed is just the creation mode tutorial
#buttons on this embed allow user to create/edit rooms/items
async def creation_mode(channel):
  view = discord.ui.View()
  embed= discord.Embed(title="Creation Mode", description="You can use this to edit or create new rooms. Use the buttons below to select what you want to do.", color=discord.Color.blue())
  new_room_button = CreateRoomButton("Create New Room")
  new_item_button = CreateItemButton("Create New Item")
  exit_button = ExitButton("Exit", channel)
  view.add_item(new_room_button)
  view.add_item(new_item_button)
  view.add_item(exit_button)
  return (embed, view)

#deactivated valentines function
async def cupid_embed(user):
  embed = discord.Embed(title="Valentines Event Sign-Up")
  view = discord.ui.View()
  if cupid.find_one({"disc": user}):
    embed.description = "You have already signed up for the Valentines Event. If you submit this form again, it will overwrite your previous valentines sign-up."
    cupid_button = CupidButton(label="I understand, I want to resubmit")
    view.add_item(cupid_button)
  else:
    embed.description = "Please only sign up for this event if you plan to write something for someone else. It is a few thousand words over three weeks, and if you're not up for that please don't sign up. If something comes up, that's OK just let Ironically-Tall know so a replacement can be written"
    cupid_button = CupidButton(label="I understand, I want to sign up")
    view.add_item(cupid_button)
  return (embed, view)

#can be used to give any player a new discord role
async def give_role(interaction, role):
  guild = interaction.guild
  id = interaction.user.id
  member = discord.utils.get(guild.members, id=id)
  print(f"id: {member.id}")
  print(f"member: {member}")
  new_role = discord.utils.get(guild.roles, name=role)
  if not role:
    print(f"ERROR - Role {role} not found")
    return
  await member.add_roles(new_role)
  print(f"role {role.name} added to {member.name}")

#old valentines function
def new_cupid(dict):
  if cupid.find_one({"disc": dict["disc"]}):
    print(f"cupid found: {dict['disc']}")
    cupid.update_one({"disc": dict["disc"]}, {"$set": dict})
    print("cupid updated")
  else:
    cupid.insert_one(dict)
    print("new cupid created")

async def delete_thread(interaction, thread_id):
  pp("deleting channel:")
  await thread_id.delete()

#used to add a new player into the database
#requires a player object that has been turned to a dict
def new_player(dict):
  users.insert_one(dict)

#returns a dict of player info for a given discord id
def get_player(name):
  player = users.find_one({"disc": name})
  if player:
    print("player found:\n" + str(player))
    return player
  else:
    return None

#returns a dict of item info for given item name
def get_item(id):
  item = items.find_one({"itemid": id})
  if item:
    return item
  else:
    return None

#creates a blank room for testing purposes
#useful for showing room structure to new database
def create_blank_room(author_name):
    room = Room("test_room", "Test Room", author_name)
    rooms.insert_one(room.__dict__)
    return room

#creates a blank adventure for testing purposes
#useful for showing adventure structure to new database
def create_blank_adventure(author):
  adventure = Adventure(name="New Advenuture", author=author, start= "", description="Blank Description")
  adventures.insert_one(adventure.__dict__)

#creates a blank item for testing purposes
#useful for showing item structure to new database
def create_blank_item(author):
    item = Item("test_item","Test Item", description="This is where the description goes", author=author)
    items.insert_one(item.__dict__)

def create_blank_key(author):
    key = Key("test_key","Test Key", description="This is where the description goes", author=author)
    keys.insert_one(key.__dict__)

#finds all the players currently in a given room
#returns a list of player discord IDs
def get_players_in_room(room):
  players_in_room = []
  players = users.find({"room": room})
  for player in players:
    players_in_room.append(player["disc"])
  return players_in_room

#returns true if player is in the game
def player_exists(name):
   return bool(users.find_one({"disc": name}))

#updates the player in the databse with a dict of info
def update_player(dict):
  print("updating player:\n")
  pp(dict)
  users.update_one({"disc": dict["disc"]}, {"$set": dict})

#creates an adventure from a dict
def create_new_adventure(dict):
  print("creating new adventure:")
  pp(dict)
  adventures.insert_one(dict)

#creates a room from a dict
def create_new_room(dict):
  print("creating new room:")
  pp(dict)
  rooms.insert_one(dict)
  id = {"id": dict["id"], "type" : "room", "displayname": dict["displayname"]}
  ids.insert_one(id)

#creates a key from a dict
def create_new_key(dict):
  print("creating new key:")
  pp(dict)
  keys.insert_one(dict)
  id = {"id": dict["id"], "type" : "key", "displayname": dict["displayname"]}
  ids.insert_one(id)

#creates an item from a dict
def create_new_item(dict):
  print("creating new item:")
  pp(dict)
  items.insert_one(dict)
  id = {"itemid": dict["itemid"]}
  ids.insert_one(id)

#updates room in databse
#optionally deletes a field in the room
def update_room(dict, delete=""):
  if delete == "":
    print("updating room:")
    pp(str(dict))
    rooms.update_one({"id": dict["id"]}, {"$set": dict})
  else:
    print("updating room:")
    pp(str(dict))
    print("deleting field from room:" + delete)
    rooms.update_one({"id": dict["id"]}, {"$set": dict}, {"$unset": {delete: ""}})

#deletes room from database
def delete_room(id):
  room = rooms.find_one({"id": id})
  if room:
    print("Deleteing room " + room["displayname"] + " with id " + room["id"])
    rooms.delete_one({"id": id})
    ids.delete_one({"id": id})
  else:
    print(f"ERROR - Room {id} does not exist")

#deletes every specified field from every room
def delete_room_fields(field):
  rooms.update_many({}, {"$unset": {field: ""}})

#deleted a player from the database by discord ID
def delete_player(name):
  users.delete_one({"disc": name})

#gets every player from the database
def get_all_players():
  return users.find()

#gets every room from the database
def get_all_rooms():
  return rooms.find()

#gets every key from the database
def get_all_keys():
  return keys.find()

#gets every item from the database
def get_all_items():
  return items.find()

#gets every adventure from the database
def get_adventures():
  return adventures.find()

#gets an adventure by name
def get_adventure(name):
  adventure = adventures.find_one({"name": name})
  if adventure:
    return adventure
  else:
    return None

#gets an adventure by discord author
def get_adventure_by_author(disc):
  adventure = adventures.find_one({"author": disc})
  if adventure:
    return adventure
  else:
    return None

#sets the kill value to true for a given player discord ID
#increments their death count by one
def kill_player(name):
  player = users.find_one({"disc": name})
  player_deaths = player["deaths"] + 1
  users.update_one({"disc": name}, {"$set": {"alive": False, "deaths": player_deaths}})

#returns a room dict of a room by room name
def get_room(id):
  room = rooms.find_one({"id": id})
  if room:
    return room
  else:
    return None

#gets requested field about a player by discord ID
#can return any valid player info
def get_player_info(name, info):
  player = users.find_one({"disc": int(name)})
  if player:
    return player[info]
  else:
    return None

#gets any player info from only the player displayname
def get_player_info_by_displayname(name, info):
  player = users.find_one({"displayname": name})
  if player:
    return player[info]
  else:
    return None

#gets the room that the player is currently in
def get_player_room(name):
  player = users.find_one({"disc" : name})
  if player:
    print(f"found player: {name}")
    room = rooms.find_one({"id": player["room"]})
    if room:
      return room
  else:
    return None

#finds an item by the displayname
def get_item_by_displayname(displayname):
  item = items.find_one({"displayname": displayname})
  if item:
    return item
  else:
    return None

#finds a key by the displayname
def get_key_by_displayname(displayname):
  key = keys.find_one({"displayname": displayname})
  if key:
    return key
  else:
    return None