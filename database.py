import os
from pprint import pprint as pp

import discord
import pymongo

from adventure import Adventure
from item import Item
from room import Room

class RoomButton(discord.ui.Button):
  def __init__(self, label, destination, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.destination = destination
    self.disabled = disabled
    self.row = row
  async def callback(self, interaction: discord.Interaction):
      await move_player(interaction, self.destination)

class CreateRoomButton(discord.ui.Button):
  def __init__(self, label, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
  async def callback(self, interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="Create a new room", description="This will create a new room with the name you provide. Fill out all of the fields to create the room. Once the room is created, you can edit it.", color=0x00ff00)
    embed.set_image(url="https://imgur.com/a/rnhBqRB")
    view = discord.ui.View()
    namefield = discord.ui.TextInput(label="Room Name", style=discord.TextStyle.short, row=0)
    confirmbutton = ConfirmButton(label="Create Room", confirm=True, action="create_room", row=1)
    action_row = discord.ActionRow()
    view.add_item(namefield)
    view.add_item(confirmbutton)
    await interaction.response.send_message(embed=embed, view=view)

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

def ping():
  try:
    mongo_client.admin.command('ping')
    print("You successfully connected to MongoDB!")
  except Exception as e:
    print(e)

database_name = os.environ['COLLECTION']
db = getattr(mongo_client, database_name)

rooms = db.rooms
users = db.users
items = db.items
adventures = db.adventures
testrooms = db.testrooms
testadventures = db.testadventures
testitems = db.testitems
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

async def creation_mode():
  view = discord.ui.View()
  embed= discord.Embed(title="Creation Mode", description="You can use this thread to edit or create new rooms. Use the buttons below to select what you want to do.", color=discord.Color.blue())
  new_room_button = CreateRoomButton("Create New Room")
  view.add_item(new_room_button)
  return (embed, view)
  

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

def new_player(dict):
  users.insert_one(dict)

def get_player(name):
  player = users.find_one({"disc": name})
  if player:
    print("player found:\n" + str(player))
    return player
  else:
    return None

def get_item(name):
  item = items.find_one({"name": name})
  if item:
    return item
  else:
    return None

def create_blank_room(author_name):
    room = Room("test_room", "Test Room", author_name)
    testrooms.insert_one(room.__dict__)
    return room

def create_blank_adventure(author):
    adventure = Adventure("Test Adventure", "test_room", author, "This is a test advenure")
    testadventures.insert_one(adventure.__dict__)

def create_blank_item():
    item = Item("test_item","Test Item", description="This is where the description goes")
    testitems.insert_one(item.__dict__)

def get_item_by_displayname(displayname):
  item = items.find_one({"displayname": displayname})
  if item:
    return item
  else:
    return None

def get_players_in_room(room):
  players_in_room = []
  players = users.find({"room": room})
  for player in players:
    players_in_room.append(player["disc"])
  return players_in_room

def player_exists(name):
   return bool(users.find_one({"disc": name}))

def update_player(dict):
  print("updating player:\n")
  pp(str(dict))
  users.update_one({"disc": dict["disc"]}, {"$set": dict})

def delete_player(name):
  users.delete_one({"disc": name})

def get_all_players():
  return users.find()

def get_all_rooms():
  return rooms.find()

def get_all_items():
  return items.find()

def get_adventures():
  return adventures.find()

def get_adventure(name):
  adventure = adventures.find_one({"name": name})
  if adventure:
    return adventure
  else:
    return None

def kill_player(name):
  users.update_one({"disc": name}, {"$set": {"alive": False}})
  
def new_game(name):
  updated_player = {"disc": name, "room": "kitchen", "alive": True, "items":[]}
  update_player(updated_player)

def get_room(name):
  room = rooms.find_one({"name": name})
  if room:
    return room
  else:
    return None

def get_player_info(name, info):
  player = users.find_one({"disc": int(name)})
  if player:
    return player[info]
  else:
    return None

def get_player_room(name):
  player = users.find_one({"disc" : name})
  if player:
    room = rooms.find_one({"name": player["room"]})
    if room:
      return room

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

  

  