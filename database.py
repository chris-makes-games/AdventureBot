import os  #stores secrets
import pathlib  #finds the commands folder
import random as rand  #random number generator
from collections import Counter  # keys list comprehension
from pprint import pprint as pp  #pretty printing

import discord
import pymongo  #mongo db api

from adventure import Adventure  #adventure class
from key import Key  #new key class, previously item
from room import Room  #room class

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

#simple button class to confirm or cancel any action
#can be placed on any embed that requires a confirmation
#action is the name of the action to be taken
class ConfirmButton(discord.ui.Button):
  def __init__(self, label, confirm, action, channel="", id=None, disabled=False, row=0, dict=None):
    super().__init__(label=label)
    self.id = id
    self.confirm = confirm
    self.action = action
    self.disabled = disabled
    self.row = row
    self.channel = channel
    self.dict = dict
    if self.confirm:
      self.style = discord.ButtonStyle.success
      self.emoji = "✅"
    else:
      self.style = discord.ButtonStyle.danger
      self.emoji = "✖️"
  #callback is for when the button is clicked
  async def callback(self, interaction: discord.Interaction):
    #must defer response or error will occur!
    await interaction.response.defer()
    #if they hit the red x it does nothing
    #embed that is asking the confirm is deleted
    if self.action == "cancel":
      await interaction.delete_original_response()
    #player wants to leave an adventure
    elif self.action == "leave":
      update_player({"disc" : interaction.user.id, "guild_thread" : None, "room" : None})
      guild = interaction.guild
      if not guild:
        await interaction.followup.send("Your adventure data has been cleared!", ephemeral=True)
        await interaction.delete_original_response()
        return
      thread_id = self.id
      if not thread_id:
        await interaction.followup.send("Your adventure data has been cleared!", ephemeral=True)
        await interaction.delete_original_response()
        return
      thread = guild.get_thread(thread_id)
      if thread:
        await thread.delete()
        await interaction.followup.send("Your adventure data has been cleared!", ephemeral=True)
        await interaction.delete_original_response()
        return
    #new room is created
    elif self.action == "new_room" and self.dict:
      create_new_room(self.dict)
      await interaction.followup.send(f"Room {self.dict['displayname']}successfully created!", ephemeral=True)
      await interaction.delete_original_response()
    #new key is created
    elif self.action == "new_key" and self.dict:
      create_new_key(self.dict)
      await interaction.followup.send(f"Key {self.dict['displayname']} successfully created!", ephemeral=True)
      await interaction.delete_original_response()
    #key deleted
    elif self.action == "delete_key" and self.dict:
      delete_key(self.dict['id'])
      await interaction.followup.send(f"Key {self.dict['displayname']} Deleted!", ephemeral=True)
    #room deleted
    elif self.action == "delete_room" and self.dict:
      delete_room(self.dict['id'])
      await interaction.followup.send(f"Room {self.dict['displayname']} deleted!", ephemeral=True)
      await interaction.delete_original_response()
    #adventure deleted
    elif self.action == "delete_adventure":
      delete_adventure(self.id)
      await interaction.followup.send(f"This would delete adventure {self.id} but it's not implemented yet! Check database.ConfirmButton", ephemeral=True)
    #player deleted
    elif self.action == "delete_player":
      await interaction.followup.send(f"This would delete player {self.id} but it's not implemented yet! Check database.ConfirmButton", ephemeral=True)
    #edit room
    elif self.action == "edit_room":
      update_room(self.dict)
      await interaction.followup.send("Room successfully updated!", ephemeral=True)
      await interaction.delete_original_response()
    #edit key
    elif self.action == "edit_key":
      update_key(self.dict)
      await interaction.followup.send("Key successfully updated!", ephemeral=True)
      await interaction.delete_original_response()
    #connect rooms together using edit
    elif self.action == "connect":
      if self.dict:
        for room_id, room_data in self.dict.items():
          rooms.update_one({"id": room_id}, {"$set": room_data})
      await interaction.followup.send("Rooms successfully connected!", ephemeral=True)
      await interaction.delete_original_response()
    #catch-all for any other action
    else:
      await interaction.followup.send("ERROR: That button has no interaction yet!", ephemeral=True)
      return

#deactivated valentines function
class CupidModal(discord.ui.Modal):
  def __init__(self, title="Valentines Event Sign-up"):
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

#secrets
db_name = os.environ['DB_NAME']
db_pass = os.environ['DB_PASS']
db_user = os.environ['DB_USER']
db_serv = os.environ['DB_SERVER']

#url for database connection
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
keys = db.keys
adventures = db.adventures
ids = db.ids
botinfo = db.botinfo
cupid = db.cupid

#lists for generating a random ID
all_numbers = ["0️", "1️", "2️", "3️", "4️", "5" ,"6️", "7️", "8️", "9️"]
all_upper_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
all_lower_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

#creates an ID that does not exist in the master ID document
#optionally allows you to generate more IDs at once
def generate_unique_id():
  all_characters = all_numbers + all_upper_letters + all_lower_letters
  id = []
  found_id = None
  banned = ids.find_one({"id": "BANNED"})
  finished_id = ""
  while len(id) < 4:
    r = rand.choice(all_characters)
    id.append(r)
    if len(id) < 4:
      continue
    if len(id) == 4:
      finished_id = "".join(id)
      found_id = ids.find_one({"id": finished_id})
    if found_id:
      print("wow, one in ~14 million chance of a duplicate id!")
      print(id)
      id = []
    elif finished_id in banned["words"]:
      print("wow, one in ~14 million chance of a swear word being generated as an ID")
      print(id)
      id = []
  return finished_id

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

#removes a command from the inactive list
def activate_command(command):
  document = botinfo.find_one({"commands": "deactivated"})
  if document:
    document["inactive"].remove(command)
    botinfo.update_one({"commands": "deactivated"}, {"$set": document})

#adds a command to the inactive list
def deactivate_command(command):
  document = botinfo.find_one({"commands": "deactivated"})
  if document:
    document["inactive"].append(command)
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
  admin_commands = ["register", "load", "unload", "reload", "sync", "updaterooms", "ping", "activate", "deactivate", "newassistant", "newmaintainer", "updaterooms", "fixall"]
  for cmd_file in CMDS_DIR.glob("*.py"):
    if cmd_file.name != "__init__.py" and cmd_file.name[:-3] not in admin_commands:
      all_commands.append(cmd_file.name[:-3])
  return all_commands

#gives player key in room if applicable
#adds keys to history if applicable
def process_player_keys(found_keys, current_keys, history):
  new_keys = current_keys
  new_history = history
  for key in found_keys:
    key = keys.find_one({"id": key.key})
    number = key.value
    if not key:
      print("ERROR - Room key not found!")
      print(f"key {key.key} does not exist")
      continue
    if key["id"] in current_keys and not key["stackable"]:
      continue
    if key["id"] not in current_keys or key["repeating"]:
      if key["unique"] and key["id"] in history:
        continue
      new_keys.append(key["id"])
      found_keys.append(key["id"])
      if key["unique"]:
        new_history.append(key["id"])
  return found_keys, new_keys, new_history
    
#moves player to a new room
#sends an embed with the new room's description and buttons
async def move_player(interaction, destination):
  guild = interaction.guild
  player = get_player(interaction.user.id)
  new_room = get_room(destination)
  if player and new_room:
    keys = player["keys"]
    destroy = new_room["destroy"]
    history = player["history"]
    print(f"player {player['displayname']} is moving to {destination}...")
    print("keys: " + str(keys))
    print("history: " + str(history))
    newroomname = new_room["id"]
    newroomauthor = new_room["author"]
    guild = interaction.guild
    author = guild.get_member(newroomauthor).display_name
    if not author:
      author = "Unknown"
  else:
    pp("ERROR - None Object during database.moveplayer()")
    pp("player: " + str(player))
    pp("room: " + str(new_room))
    return
  #if the room has keys, process keys
  if new_room["keys"]:
    pp("keys found!" + str(new_room["keys"]))
    found_keys, new_keys, new_history = process_player_keys(new_room["keys"], player["keys"], player["history"])
  else:
    pp("no keys found!")
    new_keys = keys
    new_history = history
    found_keys = []
  #destroys keys if room needs to destroy them
  if destroy:
    print("destroying keys...")
    for key in destroy:
      if key in new_keys:
        new_keys.remove(key)
        print(f"key {key} destroyed")
  pp(f"new keys: {new_keys}")
  pp(f"new history: {new_history}")
  #adds room to history if not in history
  if new_room["id"] not in new_history:
    new_history.append(new_room["id"])
  dict = {"disc": player["disc"],"room": newroomname, "keys": new_keys, "history": new_history}
  update_player(dict)
  newroomname=new_room["displayname"]
  tuple = await embed_room(player, found_keys, newroomname, new_room, author, guild)
  embed = tuple[0]
  view = tuple[1]
  await interaction.response.edit_message(embed=embed, view=view)

#returns an inventory of the player with view
async def embed_inventory(player_dict):
  embed = discord.Embed(title="Inventory", color=0x00ff00)
  counted_keys = []
  for key in player_dict["keys"]:
    found_key = keys.find_one({"id": key})
    count = Counter(player_dict["keys"])
    plurality = count[key] > 1
    if not found_key:
      room = rooms.find_one({"id": player_dict["room"]})
      author = room["author"] if room else "Unknown"
      print(f"ERROR: key {key} does not exist!")
      embed.add_field(name=f"Key {key} does not exist!", value=f"Please let <@${author}> know.")
      continue
    if found_key["inventory"] and found_key not in counted_keys:
      if plurality:
        embed.add_field(name=f"{found_key['name']}", value=f"{found_key['discription']}\nYou have {count}" , inline=False)
      else:
        embed.add_field(name=f"{found_key['name']}", value=f"{found_key['discription']}" , inline=False)
      counted_keys.append(found_key)

  view = discord.ui.View()
  return embed, view

#returns a journal of the player with view
async def embed_journal(player_dict):
  all_keys = {}
  for key in keys.find():
    all_keys[key["id"]] = key
  print("all keys:")
  pp(all_keys)
  embed = discord.Embed(title="Journal", color=0x00ff00)
  current = player_dict["keys"]
  history = []
  for key in current:
    if key not in all_keys:
      continue
    elif all_keys[key]["journal"]:
      history.append(key)
  while len(history) > 24:
    history.pop(0)
  count = 1
  for key in player_dict["history"]:
    found_key = keys.find_one({"id": key})
    if not found_key:
      continue
    if found_key["journal"]:
      if found_key not in current:
        embed.add_field(name=f"Entry {count}", value=f"{found_key['alt_note']}" , inline=False)
      else:
        embed.add_field(name=f"Entry {count}", value=f"{found_key['note']}" , inline=False)
    count += 1

  view = discord.ui.View()
  return embed, view

#room logic comparator
async def comparator(string, keys_dict):
  try:
    #uses builtins to sanitize input
    safe_dict = keys_dict
    safe_dict['__builtins__'] = None
    result = eval(string, {"__builtins__": None}, safe_dict)
    return result
  except Exception as e:
    print(f"Error: {e}")
    return False

#sends an embed with room information and buttons for player to traverse
#returns a tuple of embed and view
async def embed_room(player_dict, new_keys, title, room_dict, author, guild, color=0):
  if color == 0:
    color = discord.Color.blue()
  keys = player_dict["keys"]
  descr = room_dict['description'].replace("\\n","\n")
  descr = descr.replace("[LIKETHIS]", "\\n")
  embed = discord.Embed(title=title, description=descr, color=color)
  embed.set_footer(text="This room was created by " + author)
  if "url" in room_dict:
    embed.set_image(url=room_dict["url"])
  elif "URL" in room_dict:
    embed.set_image(url=room_dict["URL"])
  view = discord.ui.View()
  if new_keys:
    for key_id in new_keys:
      found_key = get_key(key_id)
      if not found_key:
        print(f"ERROR - key {key_id} not found!")
        continue
      if found_key["inventory"]:
        embed.add_field(name=f"You found a {found_key['displayname']}!", value=found_key["description"], inline=False)
      if found_key["journal"]:
        embed.add_field(name="New journal entry:", value=found_key["description"], inline=False)
  if room_dict["end"]:
    if room_dict["deathnote"]:
      embed.add_field(name="You Died!", value=f"You were {room_dict['deathnote']}", inline=False)
      adventure = get_adventure_by_room(room_dict["id"])
      adventure_name = "Their adventure" if not adventure else adventure["name"]
      guild_channel = botinfo.find_one({"guild": guild.id})
      channel = guild.get_channel(guild_channel["channel"])
      member = guild.get_member(player_dict["disc"])
      embed.add_field(name="The End", value="Thanks for playing! You can /leave this adventure when you're ready", inline=False)
      await channel.send(f"{member.mention} has died during {adventure_name}! They were ||{room_dict['deathnote']}||")
    embed.add_field(name="The End", value="Thanks for playing! You can /leave this adventure when you're ready", inline=False)
    if room_dict["epilogue"]:
      embed.add_field(name="Epilogue", value="While the adventure is concluded, you may freely explore the rooms to see what you might have missed", inline=False)
    update_player({"id" : player_dict["id"], "dead": True})
    return (embed, view)
  #error for when a room has no exits but is also not an end
  if len(room_dict["exits"]) == 0 and not room_dict["end"]:
    embed.add_field(name="Exits", value="There are no exits from this room. This is the end of the line. Unless this room is broken? You might have to /leave this adventure to get out.", inline=False)
  if len(room_dict["exits"]) == 1:
    embed.add_field(
  name="You have only one option.",value="press the button below to continue:", inline=False)
  else:
    embed.add_field(name="Make a Choice", value="Click a button below to continue:", inline=False)
  for room_id in room_dict["exits"]:
    found_room = get_room(room_id)
    #no room found in database
    if not found_room:
      print(f"ERROR - room {room_id} not found!")
      continue
    #if room can only be seen once, do not show option
    if found_room["once"] and found_room["id"] in player_dict["history"]:
      continue
    #if player has items that hide the room, do not show option
    if found_room["hide"] and valid_exit(keys, found_room["hide"]):
      continue
    #if hidden, doesn't show unless they have reveal keys
    if found_room["hidden"] and not valid_exit(keys, found_room["reveal"]):
      continue
    #if player has items to lock room, show only alt text
    if found_room["lock"] and valid_exit(keys, found_room["lock"]):
      button = RoomButton(label=found_room["alt_entrance"], destination=room_id, disabled=True)
      view.add_item(button)
      continue
    #if locked, shows alt text unless they have unlock keys
    if found_room["locked"]:
      if valid_exit(keys, found_room["unlock"]):
        button = RoomButton(label=found_room["entrance"], destination=room_id)
        view.add_item(button)
        continue
      #if locked, shows only alt text
      else:
        button = RoomButton(label=found_room["alt_entrance"], destination=room_id, disabled=True)
        view.add_item(button)
        continue
    #regular room entrance if not locked or hidden
    button = RoomButton(label=found_room["entrance"], destination=room_id)
    view.add_item(button)
  return (embed, view)

#returns true if the keys fit into the lock
def valid_exit(keys, lock):
  key_counter = Counter(keys)
  lock_counter = Counter(lock)
  return all(key_counter[element] >= count for element, count in lock_counter.items())

#generic confirmation embed for yes/no
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

#deletes a given thread by id
async def delete_thread(interaction, thread_id):
  pp("deleting channel:")
  await interaction.bot.delete_thread(thread_id)

#used to add a new player into the database
#requires a player object that has been turned to a dict
def new_player(dict):
  users.insert_one(dict)

#returns a dict of player info for a given discord id
def get_player(id):
  player = users.find_one({"disc": id})
  if player:
    print("player found:")
    pp(player)
    return player
  else:
    print("player not found: " + str(id))
    return None

#returns a dict of key for given key id
def get_key(id):
  key = keys.find_one({"id": id})
  if key:
    return key
  else:
    return None

#creates a blank room for testing purposes
#useful for showing room structure to new database
def create_blank_room(author_name, room_name="Blank Room"):
    room = Room(displayname=room_name, description="You have wandered into a dark place. It is pitch black. You are likely to be eaten by a grue.", author=author_name, entrance="This text is displayed when the player is in an adjescent room.", alt_entrance="This text is displayed when the room is locked")
    rooms.insert_one(room.__dict__)
    ids.insert_one({"id": room.id, "displayname" : room.displayname, "type": "room", "author": author_name})
    return room

#creates a blank adventure for testing purposes
#useful for showing adventure structure to new database
def create_blank_adventure(author):
  adventure = Adventure(name="New Advenuture", author=author, start= "", description="Blank Description")
  adventures.insert_one(adventure.__dict__)

#creates a blank key for testing purposes
def create_blank_key(author):
    key = Key("test_key","Test Key", description="This is where the description goes", author=author)
    keys.insert_one(key.__dict__)

#finds all the players currently in a given room
#returns a list of player discord IDs
def get_players_in_room(room):
  players_in_room = []
  players = users.find({"room": room})
  for player in players:
    players_in_room.append(player["displayname"])
  return players_in_room

#gets all the players in a room thats part of the adventure
#useful for checking before editing the rooms/adventure
def get_players_in_adventure(adventure_name):
  players = []
  adventure = adventures.find_one({"name": adventure_name})
  if adventure:
    for room in adventure["rooms"]:
      for player in get_players_in_room(room):
        players.append(player)
    return players
  else:
    return None

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

#updates an adventure by dict
def update_adventure(dict):
  print("updating adventure:")
  pp(dict)
  adventures.update_one({"name": dict["name"]}, {"$set": dict})

#deletes an adventure by name
def delete_adventure(name):
  print("deleting adventure:")
  adventures.delete_one({"name": name})

#creates a room from a dict
def create_new_room(dict):
  print("creating new room:")
  pp(dict)
  rooms.insert_one(dict)
  id = {"id": dict["id"], "type" : "room", "displayname": dict["displayname"], "author": dict["author"]}
  ids.insert_one(id)
  adventure= adventures.find_one({"name": dict["adventure"]})
  if adventure:
    adventure["rooms"].append(dict["id"])
    adventures.update_one({"name": dict["adventure"]}, {"$set": adventure})
    
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

#creates new key from dict
def create_new_key(dict):
  print("creating new key:")
  pp(dict)
  keys.insert_one(dict)
  id = {"id": dict["id"], "type" : "key", "displayname": dict["displayname"], "author": dict["author"]}
  ids.insert_one(id)

#updates key in database
def update_key(dict, delete=""):
  if delete == "":
    print("updating key:")
    pp(str(dict))
    keys.update_one({"id": dict["id"]}, {"$set": dict})
  else:
    print("updating key:")
    pp(str(dict))
    print("deleting field from key:" + delete)
    keys.update_one({"id": dict["id"]}, {"$set": dict}, {"$unset": {delete: ""}})

#deletes key from database
def delete_key(id):
  key = keys.find_one({"id": id})
  if key:
    print(f"deleting key {key['displayname']}")
    keys.delete_one({"id": id})
    ids.delete_one({"id": id})
  else:
    print(f"ERROR key {id} not found")

#deletes every specified field from every room
#be careful!
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
def kill_player(disc):
  player = users.find_one({"disc": disc})
  player_deaths = player["deaths"] + 1
  users.update_one({"disc": disc}, {"$set": {"alive": False, "deaths": player_deaths}})

#returns a room dict of a room by room name
def get_room(id):
  room = rooms.find_one({"id": id})
  if room:
    return room
  else:
    return None

#returns the first adventure that has the given room
def get_adventure_by_room(room):
  adventure = adventures.find_one({"rooms": room})
  if adventure:
    return adventure
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
    print(f"found player: {name}")
    room = rooms.find_one({"id": player["room"]})
    if room:
      return room
  else:
    return None

#finds a key by the displayname
def get_key_by_displayname(displayname):
  key = keys.find_one({"displayname": displayname})
  if key:
    return key
  else:
    return None