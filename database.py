import os  #stores secrets
import pathlib  #finds the commands folder
import random as rand  #random number generator
import re
from collections import Counter  # keys list comprehension
from pprint import pprint as pp  #pretty printing

from dotenv import load_dotenv #loads environment variables

import discord
import pymongo  #mongo db api

from adventure import Adventure  #adventure class
from key import Key  #new key class, previously item
from room import Room  #room class

import ast #for safely parsing string literals

#sets the parent directory of the bot
BASE_DIR = pathlib.Path(__file__).parent
#this is the command folder directory
CMDS_DIR = BASE_DIR / "cmds"

#for .env file
load_dotenv()

#for safely parsing string literals
allowed_nodes = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.Lt, ast.Gt,
    ast.LtE, ast.GtE, ast.Eq, ast.NotEq, ast.Compare, ast.BoolOp, ast.And, ast.Or, ast.Not
}


#persistent view for featured suggestion button
class FeatureView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
    self.id = "AdventureBotFeatureView"
    if not views.find_one({"id": self.id}):
      views.insert_one({"id": self.id,
                        "feature" : "AdventureBotFeatureView"
      })



#persistentview custom class
class PersistentView(discord.ui.View):
  def __init__(self, message_id, id=None):
    super().__init__(timeout=None)
    self.message_id = message_id
    if id:
      self.id = id
    if not views.find_one({"id": self.id}):
      views.insert_one({"id": self.id,
                        "message_id" : self.message_id
      })
    else:
      all_buttons = buttons.find({"message_id" : self.message_id})
    #need to add button data to database, load them in by type
      if all_buttons:
        new_button = None
        for button in all_buttons:

          print(f"adding button: {button["type"]}")

          if button["type"] == "room":
            continue
            new_button = RoomButton()
          elif button["type"] == "confirm":
            continue
            new_button = ConfirmButton()
          elif button["type"] == "key":
            continue
            new_button = KeyButton()
          elif button["type"] == "cupid":
            continue
            new_button = CupidButton()
          elif button["type"] == "gift":
            continue
            new_button = GiftButton()
          elif button["type"] == "feature":
            continue
            new_button = FeatureButton()


#button class for allowing the player to traverse rooms
#button sends player to destination room when clicked
class RoomButton(discord.ui.Button):
  def __init__(self, label, destination, message_id, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.destination = destination
    self.disabled = disabled
    self.row = row
    self.custom_id = new_persistent_button("room", message_id)
    self.message_id = message_id
  async def callback(self, interaction: discord.Interaction):
    view = self.view
    if view:
      views.delete_one({"id": view.id})
    buttons.delete_many({"message_id": self.message_id})
    await interaction.response.defer()
    await move_player(interaction, self.destination)

#button class for inventory and journal buttons
#button opens a journal or inventory and closes the current room
class KeyButton(discord.ui.Button):
  def __init__(self, button_type, playerdict, message_id, disabled=False, row=1,):
    if button_type == "inventory":
      label = "Inventory"
      emoji = "🎒"
    elif button_type == "journal":
      label = "Journal"
      emoji = "📜"
    else:
      pp("ERROR - Keybutton must have type of inventory or journal")
      label = "ERROR"
      emoji = "❌"
    super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.gray)
    self.button_type = button_type
    self.disabled = disabled
    self.row = row
    self.playerdict = playerdict
    self.message_id = message_id
    self.custom_id = new_persistent_button("key", message_id)
  async def callback(self, interaction: discord.Interaction):
    view = self.view
    if view:
      views.delete_one({"id": view.id})
    buttons.delete_many({"message_id": self.message_id})
    await open_menu(interaction, self.playerdict, self.button_type)

#simple button class to confirm or cancel any action
#can be placed on any embed that requires a confirmation
#action is the name of the action to be taken
class ConfirmButton(discord.ui.Button):
  def __init__(self, label, confirm, action, message_id, channel="", id=None, disabled=False, row=0, dict=None):
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
    self.message_id = message_id
    self.custom_id = new_persistent_button("confirm", message_id)
  #callback is for when the button is clicked
  async def callback(self, interaction: discord.Interaction):
    #must defer response or error will occur!
    await interaction.response.defer()
    #removes persistent button ID
    view = self.view
    if view:
      views.delete_one({"id": view.id})
    buttons.delete_many({"message_id": self.message_id})
    #nothing happens if they hit red X
    if self.action == "cancel":
      await interaction.delete_original_response()
    #player wants to leave an adventure
    elif self.action == "leave":
      try:
        update_player({"disc" : interaction.user.id, "play_thread" : None, "room" : None, "history" : [], "alive" : True, "keys" : {}})
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
          return
      except Exception as e:
        await interaction.followup.send(f"ERROR: Failed to leave adventure! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
    #new room is created
    elif self.action == "new_room" and self.dict:
      try:
        create_new_room(self.dict)
        #adds room ID to adventure's list of rooms
        adventure_dict = get_adventure(self.dict["adventure"])
        if adventure_dict:
          adventure_dict["rooms"].append(self.dict["id"])
          update_adventure(adventure_dict)
        else:
          await interaction.followup.send("ERROR: Failed to create new room! The adventure it's being created for doesn't exist.", ephemeral=True)
          return
        await interaction.followup.send(f"Room {self.dict['displayname']} successfully created!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Failed to create room! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #new key is created
    elif self.action == "new_key" and self.dict:
      try:
        create_new_key(self.dict)
        await interaction.followup.send(f"Key {self.dict['displayname']} successfully created!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Failed to create key! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #key deleted
    elif self.action == "delete_key":
      try:
        delete_key(self.id)
        await interaction.followup.send(f"Key {self.id} Deleted!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Key was not deleted! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #room deleted
    elif self.action == "delete_room":
      try:
        delete_room(self.id)
        await interaction.followup.send(f"Room {self.id} deleted!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Room was not deleted! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #adventure edited
    elif self.action == "edit_adventure":
      try:
        edit_adventure(self.id, self.dict)
        await interaction.followup.send(f"Adventure {self.id} edited!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Adventure was not edited! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #adventure deleted
    elif self.action == "delete_adventure":
      try:
        delete_adventure(self.id)
        all_players = get_players_in_adventure(self.id)
        all_keys = keys.find({"adventure" : self.id})
        guild = interaction.guild
        if all_players:
          for player in all_players:
            if guild:
              thread = guild.get_thread(player["thread"])
              if thread:
                print(f"deleting game thread for player {player}...")
                await thread.delete()
            print(f"moving player {player} out of adventure {self.id}...")
            update_player({"disc" : player, "play_thread" : None, "room" : None, "history" : [], "alive" : True, "keys" : {}})
        if all_keys:
          print("deleting all keys in adventure...")
          for key in all_keys:
            delete_key(key["id"])
        await interaction.followup.send(f"Adventure {self.id} deleted!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Adventure was not deleted! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #player deleted
    elif self.action == "delete_player":
      try:
        delete_player(self.id)
        await interaction.followup.send(f"Player {self.id} successfully deleted!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Player was not deleted! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #edit room
    elif self.action == "edit_room":
      try:
        update_room(self.dict)
        await interaction.followup.send("Room successfully updated!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Room update failed! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #edit key
    elif self.action == "edit_key":
      try:
        update_key(self.dict)
        await interaction.followup.send("Key successfully updated!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Key update failed! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #connect one or more rooms together
    elif self.action == "connect" and self.dict:
      print("connecting rooms...")
      try:
        rooms = connect_rooms(self.dict)
        print("Rooms connected!")
        if len(rooms) == 1:
          await interaction.followup.send(f"Room {''.join(rooms)} connected to itself!", ephemeral=True)
        else:
          await interaction.followup.send(f"Rooms successfully connected:\n{', '.join(rooms)}", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Rooms connection failed! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #overwrite player data
    elif self.action == "overwrite_player" and self.dict:
      try:
        update_player(self.dict)
        await interaction.followup.send("Player successfully overwritten!", ephemeral=True)
        await interaction.delete_original_response()
      except Exception as e:
        await interaction.followup.send(f"ERROR: Player update failed! There was an issue with the button press:\n{e}", ephemeral=True)
        print(e)
        await interaction.delete_original_response()
    #removes someone from gist exchange event
    elif self.action == "remove_gifts":
      try:
        await remove_gift(self.id, interaction)
        await interaction.followup.send("You have been successfully removed from the event!", ephemeral=True)
      except Exception as e:
        await interaction.followup.send(f"Error!\n{e}", ephemeral=True)
      await interaction.delete_original_response()
    #removes someone from valentines event
    elif self.action == "remove_valentines":
      try:
        await remove_valentine(self.id, interaction)
        await interaction.followup.send("You have been successfully removed from the event!", ephemeral=True)
      except Exception as e:
        await interaction.followup.send(f"Error!\n{e}", ephemeral=True)
      await interaction.delete_original_response()
    elif self.action == "feature":
      try:
        await new_feature(self.dict)
        await give_role(interaction=interaction, role="Feature Suggester")
        await interaction.followup.send("Your story suggestion was a success! Stay tuned for the voting process.", ephemeral=True)
      except Exception as e:
        await interaction.followup.send(f"Error!\n{e}", ephemeral=True)
      await interaction.delete_original_response()
    #catch-all for any other action
    else:
      await interaction.followup.send(f"ERROR: That button has no interaction yet! Check database/confirmbutton\nAction:\n`{self.action}`", ephemeral=True)
      return
    
#modal to suggest featured stories
class FeatureModal(discord.ui.Modal):
  def __init__(self, title="Suggest a story to be featured"):
    super().__init__(title=title)

    self.story = discord.ui.TextInput(label="Story URL", placeholder="Paste the story URL", style=discord.TextStyle.short, required=True)
    self.desc = discord.ui.TextInput(label="Share why the story should be featured", placeholder="", style=discord.TextStyle.long, required=True)
    self.add_item(self.story)
    self.add_item(self.desc)
    self.words = ["https:", "sizefiction.net", "story", "show"]
  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    url_parsed = self.story.value.split("/")
    story_number = url_parsed[-1]
    url_parsed.remove(story_number)
    for word in url_parsed:
      if word == "":
        continue
      if word not in self.words:
        await interaction.followup.send(f"{interaction.user.mention}, that does not appear to be a valid sizefiction story. Please copy-paste a story URL.", ephemeral=True)
        return
    info = feature.find_one({"info" : "admin"})
    if not story_number.isdigit():
      await interaction.followup.send(f"{interaction.user.mention}, that does not appear to be a valid sizefiction story. Please copy-paste a story URL.", ephemeral=True)
      return
    found_user = list(feature.find({"user" : interaction.user.id}))
    submissions = len(found_user)
    if story_number in info["current_features"]:
      await interaction.followup.send(f"{interaction.user.mention}, that story is currently being featured! Please submit a different story.", ephemeral=True)
      return
    if story_number in info["last_features"]:
      await interaction.followup.send(f"{interaction.user.mention}, that story was featured recently, please submit a different story!", ephemeral=True)
      return
    if found_user:
      if submissions > 2:
        await interaction.followup.send(f"{interaction.user.mention}, you have already submitted three stories to be featured, please wait until the next feature cycle!", ephemeral=True)
        return
      for found_story in found_user:
        if story_number == found_story["number"]:
          await interaction.followup.send(f"{interaction.user.mention}, you have already submitted that story to be featured, please submit a different story!", ephemeral=True)
          return
    dict = {"user": interaction.user.id, "number": story_number, "desc": self.desc.value}
    if submissions < 3:
      limit = 2 - submissions
      if limit == 1:
        limit_string = f"You will be able to submit {limit} more story after this one"
      else:
        limit_string = f"You will be able to submit {limit} more stories after this one"
    else:
      limit_string = "This will be your final submission for the featured section vote"
    new_view = PersistentView(interaction.id)
    new_button = ConfirmButton(message_id=interaction.id, label="Looks good, submit!", confirm=True, action="feature", dict=dict)
    cancel_button = ConfirmButton(message_id=interaction.id, label="Cancel", confirm=False, action="cancel")
    new_view.add_item(new_button)
    new_view.add_item(cancel_button)
    await interaction.followup.send(f"{interaction.user.mention} You are about to suggest this story to be featured:\nhttps://sizefiction.net/story/show/{story_number}\nDiscord should automatically load a preview, otherwise you may have entered the wrong URL. Is this the correct story? Confirm using the buttons below. {limit_string}.", view=new_view, ephemeral=True)

#deactivated valentines function
class CupidModal(discord.ui.Modal):
  def __init__(self, title="Valentines Event Sign-up"):
    super().__init__(title=title)
    self.likes = discord.ui.TextInput(label="What sizey things do you enjoy?", placeholder="Please include a brief description of scenarios, genders, and sizes", style=discord.TextStyle.long, required=True)
    self.limits = discord.ui.TextInput(label="What should your valentine stay away from?", placeholder="These topics will not be included in the gift you recieve. Everything else is fair game", style=discord.TextStyle.long, required=True)
    self.willing = discord.ui.TextInput(label="What topics are you comfortable working with?", placeholder="Please include any limits you may have in making your valentine.", style=discord.TextStyle.long, required=True)
    self.add_item(self.likes)
    self.add_item(self.limits)
    self.add_item(self.willing)
  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    dict = {"disc": interaction.user.id, "displayname" : interaction.user.display_name, "likes": self.likes.value, "limits": self.limits.value, "willing": self.willing.value}
    edit_mode = False
    if cupid.find_one({"disc" : interaction.user.id}):
      edit_mode = True
    new_cupid(dict)
    if edit_mode:
      await interaction.followup.send(f"{interaction.user.mention} Your preferences have been updated!", ephemeral=True)
    else:
      await give_role(interaction, "Valentine")
      await interaction.followup.send(f"{interaction.user.mention} You have signed up for the Valentines Event! Please wait until FEB 14th to recieve your secret valentine. If you have questions, please DM Ironically-Tall. You may change your info by typing `/valentine` again. Thank you for participating!!", ephemeral=True)
    await interaction.delete_original_response()

#new gifts modal for winter event
class GiftModal(discord.ui.Modal):
  def __init__(self, title="Gift Exchange Event Sign-up"):
    super().__init__(title=title)
    self.likes = discord.ui.TextInput(label="What sizey things do you enjoy?", placeholder="Please include a brief description of scenarios, genders, and sizes", style=discord.TextStyle.long, required=True)
    self.limits = discord.ui.TextInput(label="What do you NOT want to see in your gift?", placeholder="These topics will not be included in the gift you recieve. Everything else is fair game", style=discord.TextStyle.long, required=True)
    self.willing = discord.ui.TextInput(label="What are you willing to create?", placeholder="Which topics/themes are you comfortable/uncomfortable working with? Ironically-tall will do his best", style=discord.TextStyle.long, required=True)
    self.add_item(self.likes)
    self.add_item(self.limits)
    self.add_item(self.willing)
  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    dict = {"disc": interaction.user.id, "displayname" : interaction.user.display_name, "likes": self.likes.value, "limits": self.limits.value, "willing": self.willing.value}
    edit_mode = False
    if gifts.find_one({"disc" : interaction.user.id}):
      edit_mode = True
    new_gift(dict)
    if edit_mode:
      await interaction.followup.send(f"{interaction.user.mention} Your preferences have been updated!", ephemeral=True)
    else:
      await give_role(interaction, "Giver of Gifts")
      await interaction.followup.send(f"{interaction.user.mention} You have signed up for the gifts exchange event! Please wait until Dec 22nd to recieve your secret gifts recipient. If you have questions, please DM Ironically-Tall. You may change your info by typing `/gift` again. Thank you for participating!!", ephemeral=True)
    await interaction.delete_original_response()

#featured stories submission button
class FeatureButton(discord.ui.Button):
  def __init__(self, label, custom_id, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.success)
    self.custom_id = "AdventureBotFeatureButton"
    self.disabled = disabled
    self.emoji = "🔎"
    self.row = row
  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(FeatureModal())

#new gifts button
class GiftButton(discord.ui.Button):
  def __init__(self, label, message_id, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
    self.emoji = "🎁"
    self.message_id = message_id
    self.custom_id = new_persistent_button("gift", message_id)
  async def callback(self, interaction: discord.Interaction):
    view = self.view
    if view:
      views.delete_one({"id": view.id})
    buttons.delete_many({"message_id": self.message_id})
    await interaction.response.send_modal(GiftModal())

#deactivated valentines function
class CupidButton(discord.ui.Button):
  def __init__(self, label, message_id, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.disabled = disabled
    self.row = row
    self.message_id = message_id
    self.custom_id = new_persistent_button("cupid", message_id)
  async def callback(self, interaction: discord.Interaction):
    view = self.view
    if view:
      views.delete_one({"id": view.id})
    buttons.delete_many({"message_id": self.message_id})
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
feature = db.feature
botinfo = db.botinfo
cupid = db.cupid
gifts = db.gift
buttons = db.buttons
views = db.views

#lists for generating a random ID
all_numbers = ["0", "1", "2", "3", "4", "5" ,"6", "7", "8", "9"]
all_upper_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
all_lower_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
all_chars = all_numbers + all_lower_letters + all_upper_letters

#creates an ID that does not exist in the master ID document
#optionally allows you to generate more IDs at once
def generate_unique_id():
  banned = ids.find_one({"id": "BANNED"})
  finished_id = random_six()
  found_id = ids.find_one({"id": finished_id})
  while found_id:
    print("wow, one in ~14 million chance of a duplicate id!")
    print(finished_id)
    finished_id = random_six()
    found_id = ids.find_one({"id": finished_id})
  while finished_id in banned["words"]:
    print("wow, one in ~14 million chance of a swear word being generated as an ID")
    print(id)
    finished_id = random_six()
  return finished_id

#generates a string of six semi-random characters
def random_six():
  r1 = rand.choice(all_numbers)
  r2 = rand.choice(all_upper_letters)
  r3 = rand.choice(all_lower_letters)
  l1 = list(r1 + r2 + r3)
  rand.shuffle(l1)
  l1 = "".join(l1)
  r1 = rand.choice(all_numbers)
  r2 = rand.choice(all_upper_letters)
  r3 = rand.choice(all_lower_letters)
  l2 = list(r1 + r2 + r3)
  rand.shuffle(l2)
  l2 = "".join(l2)
  return l1 + l2

def random_persistent_id(length):
  while True:
    new_ID = []
    for character in range(length):
      character = rand.choice(all_chars)
      new_ID.append(character)
    new_ID = "AdventureBot" + "".join(new_ID)
    found_button = buttons.find_one({"id": new_ID})
    if found_button:
      print("Wow! You generated a duplicate ID somehow!")
      continue
    else:
      return new_ID

#function for persistent button unique IDs
def new_persistent_button(type, message_id):
    new_ID = random_persistent_id(32)
    buttons.insert_one({"button_id" : new_ID,
                        "message_id" : message_id,
                        "type" : type
                          })
    return new_ID

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

#checks if the channel is registered
def check_channel(channel_id, guild_id):
  channel_info = botinfo.find_one({"channel": channel_id})
  if not channel_info:
    print(f"channel info not found!\n{channel_id}\n{guild_id}")
    return False
  return guild_id == channel_info["guild"]

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
  architect_commands = ["architect","newroom", "newkey", "connectrooms", "editroom", "editkey", "deleteroom", "deletekey", "map", "newadventure", "preview"]
  admin_commands = ["cupid", "register", "load", "unload", "reload", "sync", "updaterooms", "ping", "activate", "deactivate", "newassistant", "newmaintainer", "updaterooms", "fixall", "viewall"]
  for cmd_file in CMDS_DIR.glob("*.py"):
    if cmd_file.name != "__init__.py" and cmd_file.name[:-3] not in admin_commands and cmd_file.name[:-3] not in architect_commands:
      all_commands.append(cmd_file.name[:-3])
  return all_commands

#returns regular commands plus architect commands
def get_architect_commands():
  all_commands = []
  admin_commands = ["cupid", "register", "load", "unload", "reload", "sync", "updaterooms", "ping", "activate", "deactivate", "newassistant", "newmaintainer", "updaterooms", "fixall", "viewall"]
  for cmd_file in CMDS_DIR.glob("*.py"):
    if cmd_file.name != "__init__.py" and cmd_file.name[:-3] not in admin_commands:
      all_commands.append(cmd_file.name[:-3])
  return all_commands

#gives player key in room if applicable
#adds keys to history if applicable
#found_keys and current_keys are now dicts
#histories are still lists of IDs
def process_player_keys(found_keys, current_keys, history, new_room):
  print("found keys:")
  pp(found_keys)
  print("current keys:")
  pp(current_keys)
  new_keys = current_keys
  new_history = history
  new_found_keys = {}
  errors = []
  #key, value pair in dict of found keys
  for key_id, key_amount in found_keys.items():
    key = keys.find_one({"id": key_id})
    #skips if no such key by that ID
    if not key:
      print("ERROR - Room key not found!")
      print(f"key {key_id} does not exist")
      errors.append(f"Key `{key_id}` does not exist!\nPlease notify the room author!")
      continue
    #skips key if player has one already and key isn't stackable
    if key["id"] in current_keys and not key["stackable"]:
      continue
    #skips if player has seen this key from this room before and key isn't repeating
    if key["id"] in history and new_room in history and not key["repeating"]:
      continue
    #skips if player has seen that unique key
    if key["id"] in history and key["unique"]:
      continue
    #succeeds if player has one or more keys and key is stackable/repeating
    if key["id"] in current_keys and key["stackable"]:
      #increments the keys if player can have more
      new_amount = current_keys[key_id] + key_amount
      new_keys.update({key_id : new_amount})
      new_found_keys.update({key_id : key_amount})
      if key["id"] not in history:
        new_history.append(key["id"])
    #adds key to player if they meet all other requirements
    else:
      new_keys.update({key_id : key_amount})
      new_found_keys.update({key_id : key_amount})
      if key["id"] not in history:
        new_history.append(key["id"])
  print("new found keys:")
  pp(found_keys)
  print("new current keys:")
  pp(current_keys)
  print("new history:")
  pp(new_history)
  return new_found_keys, new_keys, new_history, errors

#when one of the menu buttons are clicked, opens the appropriate embed
async def open_menu(interaction, playerdict, type):
  if type == "inventory":
    await embed_inventory(interaction, playerdict)
  elif type == "journal":
    await embed_journal(interaction, playerdict)
    
#moves player to a new room
#sends an embed with the new room's description and buttons
async def move_player(interaction, destination):
  #removes button from original message
  pp(interaction.data)
  await interaction.edit_original_response(view=None)

  #message attributes
  guild = interaction.guild
  player = get_player(interaction.user.id)
  new_room = get_room(destination)
  errors =[]
  if player and new_room:
    keys = player["keys"]
    destroy = new_room["destroy"]
    history = player["history"]
    print(f"player {player['displayname']} is moving to {destination}...")
    print("keys: " + str(keys))
    print("history: " + str(history))
    newroomname = new_room["id"]
    newroomauthor = new_room["author"]
    author = guild.get_member(newroomauthor).display_name
    if not author:
      author = "Unknown"
  else:
    pp("ERROR - None Object during database.moveplayer()")
    pp("player: " + str(player))
    pp("room: " + str(new_room))
    await interaction.followup.send(f"None Object during database.moveplayer(), room could not be created!\n\nplayer:\n{str(player)}\nroom:\n{str(new_room)}", ephemeral=True)
    return
  #if the room has keys, process keys
  if new_room["keys"]:
    pp("keys found!" + str(new_room["keys"]))
    found_keys, new_keys, new_history, errors = process_player_keys(new_room["keys"], player["keys"], player["history"], new_room["id"])
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
        destroy_amount = destroy[key]
        new_keys[key] = new_keys[key] - destroy_amount
        print(f"{destroy_amount} of {key} destroyed")
  pp(f"new keys: {new_keys}")
  pp(f"new history: {new_history}")
  #adds room to history if not in history
  if new_room["id"] not in new_history:
    new_history.append(new_room["id"])
  dict = {"disc": player["disc"],"room": newroomname, "keys": new_keys, "history": new_history}
  update_player(dict)
  newroomname=new_room["displayname"]
  tuple = await embed_room(interaction.id, player, found_keys, newroomname, new_room, author, guild)
  single_embed = tuple[0]
  view = tuple[1]
  leftovers = tuple[2]
  #if the room description does not fit in the embed, it will have leftover
  if leftovers:
    length = 1
    print(len(leftovers))
    for leftover in leftovers:
      if length == 1:
        embed = discord.Embed(title=single_embed.title, description=leftover)
      else:
        embed = discord.Embed(title=f"{single_embed.title} continued", description=leftover)
      #sends embed without the view/buttons if the embed isn't the last one
      print(length)
      if length < len(leftovers):
        await interaction.followup.send(embed=embed)
      else:
        print("adding final embed")
        await interaction.followup.send(embed=embed, view=view)
      length += 1
  #sends basic embed if no leftovers
  else:
    await interaction.followup.send(embed=single_embed, view=view)
  if errors:
    error_message = "ERRORS FOUND IN ROOM:\n"
    for error in errors:
      error_message += error + "\n"
    await interaction.followup.send(error_message, ephemeral=True)

#returns an inventory of the player with view
async def embed_inventory(interaction, player_dict):
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
  view = PersistentView(interaction.id)
  await interaction.response.edit_message(embed=embed, view=view)

#returns a journal of the player with view
async def embed_journal(interaction, player_dict):
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
  view = PersistentView(interaction.id)
  await interaction.response.edit_message(embed=embed, view=view)

#sends an embed with room information and buttons for player to traverse
#returns a tuple of embed and view, with a leftover list
#leftover list is list of strings over the character limit for embeds
async def embed_room(interaction_id, player_dict, new_keys, title, room_dict, author, guild, color=0):
  if color == 0:
    color = discord.Color.blue()
  keys = player_dict["keys"]
  descr = room_dict['description'].replace("\\n","\n")
  descr = descr.replace("[LIKETHIS]", "\\n")
  leftover_list = []
  if len(descr) > 4000:
    descr, leftover_list = room_extender(descr)
  embed = discord.Embed(title=title, description=descr, color=color)
  embed.set_footer(text="This room was created by " + author)
  if "url" in room_dict:
    embed.set_image(url=room_dict["url"])
  elif "URL" in room_dict:
    embed.set_image(url=room_dict["URL"])
  view = PersistentView(interaction_id)
  adventure = get_adventure_by_room(room_dict["id"])
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
      adventure_name = "Their adventure" if not adventure else adventure["name"].title()
      guild_channel = botinfo.find_one({"guild": guild.id})
      channel = guild.get_channel(guild_channel["channel"])
      member = guild.get_member(player_dict["disc"])
      embed.add_field(name="The End", value="Thanks for playing! You can /leave this adventure when you're ready", inline=False)
      await channel.send(f"{member.mention} has died during {adventure_name}! They were ||{room_dict['deathnote']}||")
    embed.add_field(name="The End", value="Thanks for playing! You can /leave this adventure when you're ready", inline=False)
    if adventure and adventure["epilogue"]:
      embed.add_field(name="Epilogue", value="While the adventure is concluded, you may freely explore the rooms to see what you might have missed", inline=False)
    update_player({"id" : player_dict["id"], "dead": True})
    return (embed, view, leftover_list)
  #error for when a room has no exits but is also not an end
  if len(room_dict["exits"]) == 0 and not room_dict["end"]:
    embed.add_field(name="Exits", value="There are no exits from this room. This is the end of the line. Unless this room is broken? You might have to /leave this adventure to get out.", inline=False)
  if len(room_dict["exits"]) == 1:
    embed.add_field(
  name="You have only one option.",value="press the button below to continue", inline=False)
  else:
    embed.add_field(name="Make a Choice", value="Click a button below to continue", inline=False)
  for room_id in room_dict["exits"]:
    #puts a button on each of 4 available rows
    current_row = 0
    #prevents more than 4 buttons
    if current_row > 3:
      break
    found_room = get_room(room_id)
    #no room found in database
    if not found_room:
      print(f"ERROR - room {room_id} not found!")
      continue
    #if room can only be seen once, do not show option if player has been there
    if found_room["once"] and found_room["id"] in player_dict["history"]:
      continue
    #if player has items that hide the room, do not show option
    if found_room["hide"] and valid_exit(keys, found_room["hide"]):
      continue
    #if hidden, doesn't show unless they have reveal keys
    if found_room["hidden"] and not valid_exit(keys, found_room["reveal"]):
      continue
    #if player has items to lock room, show alt text on locked button
    if found_room["lock"] and valid_exit(keys, found_room["lock"]):
      button = RoomButton(label=found_room["alt_entrance"], destination=room_id, message_id=interaction_id, disabled=True, row=current_row)
      view.add_item(button)
      continue
    #if locked, unlocks is player has the keys
    if found_room["locked"]:
      if valid_exit(keys, found_room["unlock"]):
        print("keys:")
        pp(keys)
        button = RoomButton(label=found_room["entrance"], destination=room_id, message_id=interaction_id, row=current_row)
        view.add_item(button)
        continue
      #if still locked, shows alt text on locked button
      else:
        button = RoomButton(label=found_room["alt_entrance"], destination=room_id, message_id=interaction_id, disabled=True, row=current_row)
        view.add_item(button)
        continue
    #regular room entrance if not locked or hidden or anything else
    button = RoomButton(label=found_room["entrance"], destination=room_id, message_id=interaction_id, row=current_row)
    view.add_item(button)
  return (embed, view, leftover_list)

#if room description is too long, split it into smaller pieces
def room_extender(long_string):
  new_long_string = long_string[:4000]
  leftovers = []
  paragraph_number = 0
  while len(long_string) > 0:
    if len(long_string) > 4000:
      #Find the last space within the first 40 characters
      split_index = long_string.rfind(" ", 0, 4000)
      if split_index == -1:
        split_index = 4000
      leftovers.append(long_string[:split_index])
      long_string = long_string[split_index:].lstrip() 
    else:
      leftovers.append(long_string)
      break
    paragraph_number += 1
  return new_long_string, leftovers
    
#safely parse string literals
def safe_parse(expression):
  try:
    node = ast.parse(expression, mode='eval')
    return all(isinstance(n, tuple(allowed_nodes)) for n in ast.walk(node))
  except Exception as e:
    print(e)
    return False

#returns true if the keys in dict fit into the lock list of expressions
def valid_exit(keys_dict, lock_list):
  #returns false if the room has no way to unlock
  if not lock_list:
    return False
  for expression in lock_list:
    if not safe_parse(expression):
      print(f"ERROR! Unsafe expression detected:\n{expression}")
      return False
    expr_with_vars = expression
    print(f"Original expression: {expression}")
    keys_in_expr = set(re.findall(r'\b\w+\b', expression))
    for key in keys_in_expr:
      #skips the key if it's a comparator or a number
      if key == "or" or key == "and" or key.isdigit():
        continue
      #changes the key to its value, or zero if there is no key in dict
      expr_with_vars = re.sub(rf'\b{key}\b', str(keys_dict.get(key, 0)), expr_with_vars)
      print(f"Replaced expression for eval: {expr_with_vars}")
    if not eval(expr_with_vars, {"__builtins__": {}}):
      return False
  return True

#generic confirmation embed for yes/no
#adds a ConfirmButton to itself at the bottom
#action is the action that the button will do
async def confirm_embed(interaction_id, confirm_text, action, channel, title="Are you Sure?", id=None, dict=None):
  embed = discord.Embed(title=title, description=confirm_text, color=discord.Color.orange())
  confirm_button = ConfirmButton(message_id=interaction_id, label="Yes", confirm=True, action=action, channel=channel, id=id, dict=dict)
  deny_button = ConfirmButton(message_id=interaction_id, label="No", confirm=False, action="cancel", channel=channel)
  view = PersistentView(interaction_id)
  view.add_item(confirm_button)
  view.add_item(deny_button)
  if action == "leave":
    embed.set_image(url="https://i.kym-cdn.com/entries/icons/mobile/000/028/033/Screenshot_7.jpg")
  return (embed, view)

#new valentine embed for winter event
async def feature_embed(interaction_id, user):

  embed = discord.Embed(title="Featured Story Suggestions")
  view = FeatureView()
  embed.description = "To be featured on the front page of sizefiction, we are taking suggestions from everyone! We will then create a poll for everyone to vote on the ones suggested. Anyone may suggest a story to be featured, and you can even suggest your own stories. All suggestions will be collected, and stories can be suggested multiple times by different people. This process is anonymous, but Ironically-Tall can access the discord data. Limit to 3 suggestions per person, per feature cycle. Please report any issues with this bot to <@267389442409496578>. He coded it, so it's his fault."
  embed.add_field(name="Submission Format", value="When you click the button below, you will be prompted to input the URL of the story. Simply copy-paste the story URL into the field.")
  feature_button = FeatureButton(custom_id="AdventureBotFeatureButton", label="Suggest a Story to be featured")
  view.add_item(feature_button)
  return (embed, view)

#new gifts embed for winter event
async def gifts_embed(interaction_id, user):
  embed = discord.Embed(title="gifts Exchange Event Sign-Up")
  view = PersistentView(interaction_id)
  if gifts.find_one({"disc": user}):
    embed.description = "You have already signed up for the gifts Exchange Event. If you submit this form again, it will overwrite your previous valentines sign-up.\nOtherwise, you may opt out of the event using the button below."
    gifts_button = GiftButton(message_id=interaction_id, label="I understand, I want to resubmit")
    remove_button = ConfirmButton(message_id=interaction_id, label="Remove me from the event", action="remove_gifts", confirm=False, id=user)
    cancel_button = ConfirmButton(message_id=interaction_id, label="Keep my already submitted info", confirm=True, action="cancel")
    view.add_item(gifts_button)
    view.add_item(cancel_button)
    view.add_item(remove_button)
  else:
    embed.description = "Please only sign up for this event if you plan to make a gifts for someone else. It is a few hours of work over three weeks, and if you're not up for that please don't sign up. If something comes up, that's OK just let Ironically-Tall know ASAP so a replacement can be created.\nPlease also respect the time and efforts of the others signing up, and if you're going to be sending something last minute at least let Ironically-Tall know. Communication is key! Any issues can be forgiven, but dissapearing will make Ironically-Tall very sad.\nYou can use this command any number of times before DEC 22nd, each time you submit the form it will re-write your preferences."
    gifts_button = GiftButton(message_id=interaction_id, label="I understand, I want to sign up")
    cancel_button = ConfirmButton(message_id=interaction_id, label="Never Mind", action="cancel", confirm=False)
    view.add_item(gifts_button)
    view.add_item(cancel_button)
  return (embed, view)

#new valentine embed for winter event
async def valentine_embed(interaction_id, user):
  embed = discord.Embed(title=":heart: Valentine's Event Sign-Up :heart:")
  view = PersistentView(interaction_id)
  if cupid.find_one({"disc": user}):
    embed.description = "You have already signed up for the Valentine's Event. If you submit this form again, it will overwrite your previous valentines sign-up.\nOtherwise, you may opt out of the event using the button below."
    cupid_button = CupidButton(message_id=interaction_id, label="I understand, I want to resubmit")
    remove_button = ConfirmButton(message_id=interaction_id, label="Remove me from the event", action="remove_valentines", confirm=False, id=user)
    cancel_button = ConfirmButton(message_id=interaction_id, label="Keep my already submitted info", confirm=True, action="cancel")
    view.add_item(cupid_button)
    view.add_item(cancel_button)
    view.add_item(remove_button)
  else:
    embed.description = "Please only sign up for this event if you plan to make a valentine for someone else. It is a few hours of work over two weeks, and if you're not up for that please don't sign up. If something comes up, that's OK just let Ironically-Tall know ASAP so a replacement can be created.\nPlease also respect the time and efforts of the others signing up, and if you're going to be sending something last minute at least let Ironically-Tall know. Communication is key! Any issues can be forgiven, but dissapearing will make Ironically-Tall very sad.\nYou can use this command any number of times before FEB 14th, each time you submit the form it will overwrite your preferences.\nPlease be explicit about what you want/don't want! Cruel? Gentle? Male? Female? Furry? Your valentine can only work with what you type!"
    gifts_button = CupidButton(message_id=interaction_id, label="I understand, I want to sign up")
    cancel_button = ConfirmButton(message_id=interaction_id, label="Never Mind", action="cancel", confirm=False)
    view.add_item(gifts_button)
    view.add_item(cancel_button)
  return (embed, view)

#can be used to give any player a new discord role
async def give_role(interaction, role):
  guild = interaction.guild
  id = interaction.user.id
  member = discord.utils.get(guild.members, id=id)
  print(f"id: {member.id}")
  print(f"member: {member}")
  new_role = discord.utils.get(guild.roles, name=role)
  if not new_role:
    print(f"ERROR - Role {role} not found")
    return
  await member.add_roles(new_role)
  print(f"role {new_role.name} added to {member.name}")

#new gifts function
def new_gift(dict):
  if gifts.find_one({"disc": dict["disc"]}):
    print(f"gifts found: {dict['disc']}")
    gifts.update_one({"disc": dict["disc"]}, {"$set": dict})
    print("gifts updated")
  else:
    gifts.insert_one(dict)
    print("new gifts created")

#remove gifts function
async def remove_gift(id, interaction):
  guild = interaction.guild
  if gifts.find_one({"disc": id}):
    print(f"gift found: {id}")
    gifts.delete_one({"disc": id})
    print("gift deleted")
    try:
      member = discord.utils.get(guild.members, id=id)
      new_role = discord.utils.get(guild.roles, name="Giver of Gifts")
      await member.remove_roles(new_role)
      print("Gift role deleted!")
    except Exception as e:
      return
  else:
    raise Exception("ERROR: Gift giver not found in database!!")
  
#remove valentine function
async def remove_valentine(id, interaction):
  guild = interaction.guild
  if cupid.find_one({"disc": id}):
    print(f"valentine found: {id}")
    cupid.delete_one({"disc": id})
    print("valentine deleted")
    try:
      member = discord.utils.get(guild.members, id=id)
      new_role = discord.utils.get(guild.roles, name="Valentine")
      await member.remove_roles(new_role)
      print("Valentine role deleted!")
    except Exception as e:
      return
  else:
    raise Exception("ERROR: Valentine not found in database!!")

#valentines function
def new_cupid(dict):
  if cupid.find_one({"disc": dict["disc"]}):
    print(f"cupid found: {dict['disc']}")
    cupid.update_one({"disc": dict["disc"]}, {"$set": dict})
    print("cupid updated")
  else:
    cupid.insert_one(dict)
    print("new cupid created")

#add featured story to database
async def new_feature(dict):
  feature.insert_one(dict)
  print("new feature created")

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

#returns a dict of key for given key id, case agnostic
def get_key(id):
  all_keys = keys.find()
  for key in all_keys:
    if key["id"].lower() == id.lower():
      return key
  return None

#creates a blank room for testing purposes, returns room object
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

#edits an adevnture by name using dict
def edit_adventure(name, dict):
  adventures.update_one({"name": name}, {"$set": dict})
    

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
  adventure = adventures.find_one({"name": adventure_name.lower()})
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
  print(f"deleting adventure: {name}")
  found_adventure = adventures.find_one({"name": name})
  found_player = found_adventure["author"]
  if found_adventure:
    for room_id in found_adventure["rooms"]:
      delete_room(room_id)
  adventures.delete_one({"name": name})
  print("Adventure deleted!")
  if found_player:
    update_player({"disc": found_player, "owned_adventures" : []})
    print("Player's owned adventures reset!")
  else:
    print("Error! Adventure owner not found!")

#creates a room from a dict
def create_new_room(dict):
  print("creating new room:")
  pp(dict)
  rooms.insert_one(dict)
  id = {"id": dict["id"], "type" : "room", "displayname": dict["displayname"], "author": dict["author"]}
  ids.insert_one(id)
  adventure= adventures.find_one({"name": dict["adventure"].lower()})
  if adventure:
    adventure["rooms"].append(dict["id"])
    adventures.update_one({"name": dict["adventure"]}, {"$set": adventure})

#connects rooms using a dict of room dicts
#returns list of displaynames of rooms that it connected
def connect_rooms(dict):
  strings = []
  for subdict in dict:
    new_room = dict[subdict]
    rooms.update_one({"id": new_room["id"]}, {"$set": new_room})
    strings.append(new_room["displayname"])
  return strings
    
#updates room in databse
#optionally deletes a field in the room
def update_room(dict, delete=""):
  #updates displalyname if changed
  if "new_displayname" in dict:
    ids.update_one({"id": dict["id"]}, {"$set": {"displayname": dict["new_displayname"]}})
  if "new_id" in dict:
    update_room_id(dict)
    print(f"updating room id {dict['id']} to {dict['new_id']}:")
    pp(dict)
    old_id = dict["id"]  
    new_id = dict["new_id"]
    dict["id"] = new_id
    del dict["new_id"]
    pp(dict)
    rooms.update_one({"id": old_id}, {"$set": dict})
    return
  elif delete == "":
    print("updating room:")
    pp(dict)
    rooms.update_one({"id": dict["id"]}, {"$set": dict})
    return
  else:
    print("updating room:")
    pp(dict)
    print("deleting field from room:" + delete)
    rooms.update_one({"id": dict["id"]}, {"$set": dict}, {"$unset": {delete: ""}})

#updates all uses of room to new ID
def update_room_id(dict):
  id = dict["id"]
  new_id = dict["new_id"]
  ids.update_one({"id": id}, {"$set": {"id": new_id}})
  all_rooms = rooms.find()
  all_adventures = adventures.find()
  print("found rooms:")
  pp(all_rooms)
  for room in all_rooms:
    if id in room["exits"]:
      print("ROOM ID FOUND IN EXIT")
      room_dict = room.copy()
      pp(room_dict)
      room_dict["exits"].remove(id)
      room_dict["exits"].append(new_id)
      pp(room_dict)
      rooms.update_one({"id": room_dict['id']}, {"$set": room_dict})
  for adventure in all_adventures:
    if id in adventure["rooms"]:
      adventure_dict = adventure.copy()
      adventure_dict["rooms"].remove(id)
      adventure_dict["rooms"].append(new_id)
      adventures.update_one({"name": adventure["name"]}, {"$set": adventure_dict})

#deletes room from database
def delete_room(id):
  room = rooms.find_one({"id": id})
  if room:
    print("Deleteing room " + room["displayname"] + " with id " + room["id"])
    rooms.delete_one({"id": id})
    print("Room deleted!")
    delete_extra_ids(id)
    print("Deleted Extra IDs!")
    ids.delete_one({"id": id})
    adventure = adventures.find_one({"name": room["adventure"].lower()})
    if adventure:
      if id in adventure["rooms"]:
        adventure["rooms"].remove(id)
      else:
        print(f"ERROR - room {id} not found in adventure {adventure['name']} during deletion")
        return
      adventures.update_one({"name": adventure["name"]}, {"$set": adventure})
    else:
      print(f"ERROR - adventure {adventure} not found during deletion")
      return
  else:
    print(f"ERROR - Room {id} does not exist to be deleted")
    return

#creates new key from dict
def create_new_key(dict):
  print("creating new key:")
  pp(dict)
  keys.insert_one(dict)
  id = {"id": dict["id"], "type" : "key", "displayname": dict["displayname"], "author": dict["author"]}
  ids.insert_one(id)
  print(f"key created! id: {dict['id']}")

#updates key in database
def update_key(dict, delete=""):
  #updates displalyname if changed
  if "new_displayname" in dict:
    ids.update_one({"id": dict["id"]}, {"$set": {"displayname": dict["new_displayname"]}})
  #updates new ids if ID is changed
  if "new_id" in dict:
    update_key_id(dict["id"], dict["new_id"])
    old_id = dict["id"]
    dict["id"] = dict["new_id"]
    del dict["new_id"]
    keys.update_one({"id": old_id}, {"$set": dict})
  elif delete == "":
    print("updating key:")
    pp(str(dict))
    keys.update_one({"id": dict["id"]}, {"$set": dict})
  else:
    print("updating key:")
    pp(str(dict))
    print("deleting field from key:" + delete)
    keys.update_one({"id": dict["id"]}, {"$set": dict}, {"$unset": {delete: ""}})

#updates all uses of key ID in database
def update_key_id(id, new_id):
  #ensures ID is not already in use
  id_check = ids.find_one({"id": new_id})
  if id_check:
    print("FATAL ERROR - ID already exists!!!")
    raise Exception ("ERROR! Old key ID not found in database to update!")
  #updates ID in IDs collection
  ids.update_one({"id": id}, {"$set": {"id": new_id}})
  all_keys = keys.find()
  all_rooms = rooms.find()
  #updates every subkey mention
  for key in all_keys:
    if id in key["subkeys"]:
      old_amount = key["subkeys"].pop(id)
      #sets subkey dict to same value as old, changing the key only
      key["subkeys"][new_id] = old_amount
      keys.update_one({"id": key["id"]}, {"$set": key})
  #updates every room mention
  for room in all_rooms:
    need_update = False
    if room["keys"] and id in room["keys"]:
      need_update = True
      old_amount = room["keys"].pop(id)
      room["keys"][new_id] = old_amount
    if room["destroy"] and id in room["destroy"]:
      need_update = True
      old_amount = room["destroy"].pop(id)
      room["destroy"][new_id] = old_amount
    #only updates the rooms that have the key
    if need_update:
      rooms.update_one({"id": room["id"]}, {"$set": room})

#deletes key from database
def delete_key(id):
  key = keys.find_one({"id": id})
  if key:
    print(f"deleting key {key['displayname']}")
    keys.delete_one({"id": id})
    delete_extra_ids(id)
    ids.delete_one({"id": id})
  else:
    print(f"ERROR key {id} not found")

#returns an ID if one is found
def get_id(id):
  all_ids = ids.find()
  for i in all_ids:
    #ids are always compared to each other in lowercase
    if i["id"].lower() == id.lower():
      return i
  return None

#deletes instances in database where ID appears
#handles removing deleted rooms from player histories and deleted items from rooms
def delete_extra_ids(id):
  found_id = ids.find_one({"id": id})
  if not found_id:
    print(f"ERROR - ID {id} not found during extra ID deletion")
    return
  print(f"deleting extra ids for {id}")
  pp(found_id)
  all_players = users.find()
  all_rooms = rooms.find()
  all_keys = keys.find()
  changed = False
  if found_id["type"] == "room":
    for player in all_players:
      #moves to next player if they're not in a room
      if not player["room"]:
        continue
      #resets player back to start room if they're inside the deleted room
      if player["room"].lower() == found_id["id"].lower():
        print(f"resetting player {player['displayname']} to start room, their room is being deleted!")
        player_adventure = get_adventure_by_room(player["room"])
        if player_adventure:
          player["room"] = player_adventure["start"]
          changed = True
        else:
          print(f"ERROR - could not find adventure for room during delete\n{player['room']}")
          return
      #removes the deleted room from the player's history
      if id in player["history"]:
        print(f"removing room {id} from player {player['displayname']}'s history")
        player["history"].remove(id)
        changed = True
      if changed:
        users.update_one({"disc": player["disc"]}, {"$set": player})
        changed = False
  elif found_id["type"] == "key":
    for room in all_rooms:
      #removes the deleted key from any room's keys where it appears
      if id in room["keys"]:
        print(f"removing key {id} from room {room['displayname']}")
        room["keys"].pop(id, None)
        rooms.update_one({"id": room["id"]}, {"$set": room})
    for key in all_keys:
      #removes mention of deleted key from any subkeys where it appears
      if id in key["subkeys"]:
        print(f"removing key {id} from subkey {key['displayname']}")
        key["subkeys"].pop(id, None)
        keys.update_one({"id": key["id"]}, {"$set": key})
    #remove key from player inventories and histories
    for player in all_players:
      if id in player["history"]:
        player["history"].remove(id)
        changed = True
      if id in player["keys"]:
        player["keys"].pop(id, None)
        changed = True
      if changed:
        users.update_one({"disc" : player["disc"]}, {"$set": player})
        changed = False
  print(f"extra ids deleted for {found_id['displayname']}!")
    
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
  all_adventures = adventures.find()
  for adventure in all_adventures:
    if adventure["name"].lower() == name.lower():
      return adventure
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

#returns a room dict of a room by room name, case agnostic
def get_room(id):
  all_rooms = rooms.find()
  for room in all_rooms:
    if room["id"].lower() == id.lower():
      return room
  return None

#returns the first adventure that has the given room, case agnostic
def get_adventure_by_room(room):
  all_adventures = adventures.find()
  for adventure in all_adventures:
    for found_room in adventure:
      if found_room.lower() == room.lower():
        return adventure
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