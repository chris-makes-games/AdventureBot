import os #stores secrets
from pprint import pprint as pp #pretty printing

import discord #discord api
import pymongo #mongo db api
import random as rand #random number generator

from adventure import Adventure #adventure class
from item import Item #item class
from room import Room #room class

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

class CreateRoomModal(discord.ui.Modal):
  def __init__(self):
    super().__init__(title="Create New Room")
    self.name = discord.ui.TextInput(label="Room Name", style=discord.TextStyle.short, required=True)
    self.description = discord.ui.TextInput(label="Room Description", style=discord.TextStyle.paragraph, required=True, placeholder="You have moved into a dark place. It is pitch black. You are likely to be eaten by a grue.")
    self.items = discord.ui.TextInput(label="Room Items", placeholder="enter item IDs, separated by commas: Fs53, 6gHj, t2WQ", required=False, style=discord.TextStyle.short)
    self.kill = discord.ui.Select(placeholder="Kill")
    self.add_item(self.name)
    self.add_item(self.description)
    #removed items from form, for now
    #self.add_item(self.items)
  async def on_submit(self, interaction: discord.Interaction):
    user_id = interaction.user.id
    room = Room(displayname= self.name.value, description = self.description.value, items = self.items.value, author=user_id)
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
    user_id = interaction.user.id
    item = Item(displayname= self.name.value, description = self.description.value, items = self.items.value, author=user_id)
    create_new_room(room.__dict__)
    await interaction.response.send_message(f"Room created:\nRoom display name: {self.name}\n description:\n{self.description}\nItems:\n{self.items}", ephemeral=True)


#WIP button class for creating a room from an embed
#generates an embed with fields for the room
#when clicked, the room making embed is sent to the channel
class CreateRoomButton(discord.ui.Button):
  def __init__(self, label, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
  #callback is for when the button is clicked
  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CreateRoomModal())

#simple button class to confirm or cancel any action
#can be placed on any embed that requires a confirmation
#action is the name of the action to be taken
class ConfirmButton(discord.ui.Button):
  def __init__(self, label, confirm, action, channel="", disabled=False, row=0):
    super().__init__(label=label)
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
    if self.action == "leave":
      await leave_game(interaction, self.channel)
    elif self.action == "cancel":
      await interaction.delete_original_response()
    elif self.action == "create_room":
      await interaction.response.send_message("Creating room... jk this isn't doing anything yet but it's working")
      return
    else:
      print("ERROR - confirmation button has no action!")
      return

db_name = os.environ['DB_NAME']
db_pass = os.environ['DB_PASS']
db_user = os.environ['DB_USER']
db_serv = os.environ['DB_SERVER']

mongo_client = pymongo.MongoClient("mongodb+srv://" + 
db_user + ":" + db_pass + "@" + db_name + db_serv)

#checks to make sure database is connected to
def ping():
  try:
    mongo_client.admin.command('ping')
    print("You successfully connected to MongoDB!")
  except Exception as e:
    print(e)

#creates the databse object in mongo_client
database_name = os.environ['COLLECTION']
db = getattr(mongo_client, database_name) #turns string to attribute

#curson objects hold document data
#function similar to dicts but are not dicts
rooms = db.rooms
users = db.users
items = db.items
adventures = db.adventures
testrooms = db.testrooms
testadventures = db.testadventures
testitems = db.testitems
ids = db.ids

#lists for generating a random ID
all_numbers = ["0️", "1️", "2️", "3️", "4️", "5" ,"6️", "7️", "8️", "9️"]
all_upper_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
all_lower_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

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
    item_object = items.find_one({"name" : item})
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
  pp("New Items:" + str(items_grouping))
  return items_grouping

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
    newroomname = new_room["name"]
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
  tuple = embed_room(inventory, new_items, "You enter the " + newroomname, new_room)
  embed = tuple[0]
  view = tuple[1]
  await interaction.response.edit_message(embed=embed, view=view)

#sends an embed with room information and buttons for player to traverse
#returns a tuple of embed and view
def embed_room(all_items, new_items, title, room, color=0):
  if color == "":
    color = discord.Color.blue()
  descr = room["description"]
  embed = discord.Embed(title=title, description=descr, color=color)
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
async def confirm_embed(confirm_text, action, channel):
  embed = discord.Embed(title="Are you Sure?", description=confirm_text, color=discord.Color.orange())
  confirm_button = ConfirmButton(label="Yes", confirm=True, action=action, channel=channel)
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
async def creation_mode():
  view = discord.ui.View()
  embed= discord.Embed(title="Creation Mode", description="You can use this thread to edit or create new rooms. Use the buttons below to select what you want to do.", color=discord.Color.blue())
  new_room_button = CreateRoomButton("Create New Room")
  view.add_item(new_room_button)
  return (embed, view)
  
#removes player from the game, deleting the database entry
#deletes the thread associated with the player's game
async def leave_game(interaction, channel):
    player = get_player(interaction.user.id)
    if player:
      pp("deleting channel: " + str(player["channel"]))
      await channel.delete()
      pp("deleting player: " + str(player["displayname"]))
      delete_player(player["disc"])
      return
    else:
        print("ERROR - Player does not exist")
        return

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
def get_item(name):
  item = items.find_one({"name": name})
  if item:
    return item
  else:
    return None

#creates a blank room for testing purposes
#useful for showing room structure to new database
def create_blank_room(author_name):
    room = Room("test_room", "Test Room", author_name)
    testrooms.insert_one(room.__dict__)
    return room

#creates a blank adventure for testing purposes
#useful for showing adventure structure to new database
def create_blank_adventure(author):
    adventure = Adventure("Test Adventure", "test_room", author, "This is a test advenure")
    testadventures.insert_one(adventure.__dict__)

#creates a blank item for testing purposes
#useful for showing item structure to new database
def create_blank_item():
    item = Item("test_item","Test Item", description="This is where the description goes")
    testitems.insert_one(item.__dict__)

#finds all the players currently in a given room
#returns a list of player discord IDs
def get_players_in_room(room):
  players_in_room = []
  players = users.find({"room": room})
  for player in players:
    players_in_room.append(player["disc"])
  return players_in_room

#updates the player in the databse with a dict of info
def update_player(dict):
  print("updating player:\n")
  pp(str(dict))
  users.update_one({"disc": dict["disc"]}, {"$set": dict})

def create_new_room(dict):
  print("creating new room:")
  pp(str(dict))
  rooms.insert_one(dict)
  id = {"id": dict["id"]}
  ids.insert_one(id)

#updates room in databse
#optionally deletes a field in the room
def update_room(dict, delete=""):
  if delete == "":
    print("updating room:")
    pp(str(dict))
    rooms.update_one({"name": dict["name"]}, {"$set": dict})
  else:
    print("updating room:")
    pp(str(dict))
    print("deleting field from room:" + delete)
    rooms.update_one({"name": dict["name"]}, {"$set": dict}, {"$unset": {delete: ""}})

def delete_room(id):
  room = rooms.find_one({"id": id})
  if room:
    print(f"Deleteing room " + room["displayname"] + " with id " + room[id])
    rooms.delete_one({"id": id})
    ids.delete_one({"id": id})
  else:
    print(f"ERROR - Room {id} does not exist")

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

#sets the kill value to true for a given player discord ID
def kill_player(name):
  users.update_one({"disc": name}, {"$set": {"alive": False}})

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

#gets the room that the player is currently in
def get_player_room(name):
  player = users.find_one({"disc" : name})
  if player:
    print(str(player))
    room = rooms.find_one({"id": player["room"]})
    if room:
      return room
  else:
    return None

#returns true if player has selected a correct exit
def check_valid_exit(name, attempt):
  player = get_player(name)
  room = get_player_room(name)
  if player and room:
    exits = room["exits"]
    secrets = room["secrets"]
    keys = room["unlockers"]
    items = player["inventory"]
    if attempt > len(exits):
      return False
    if secrets[attempt] == "Open":
      return True
    return keys[attempt] in items

  

  