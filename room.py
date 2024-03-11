import database
import discord


#button class for allowing the player to traverse rooms
#button sends player to destination room when clicked
class RoomButton(discord.ui.Button):
  def __init__(self, label, destination, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.destination = destination
    self.disabled = disabled
    self.row = row
  async def callback(self, interaction: discord.Interaction):
      await database.move_player(interaction, self.destination)

class Room:
  def __init__(
    self, dict=None,
    id="", displayname="", author=None, url="",
    description="", end=False, once=False, exits=None, items=None,
    secret=False, locked=False, keys=None, alt_text=""):
    
    if dict:
      self.id = database.generate_unique_id()
      for key, value in dict.items():
          setattr(self, key, value)
      if self.description == "":
        self.description = "NO DESCRIPTION GIVEN"
      if self.displayname == "":
        self.displayname = "NO DISPLAY NAME GIVEN"
      if self.author == None:
        self.author = "INVALID AUTHOR"
    else:
      self.id = database.generate_unique_id()
      self.description = description
      self.end = end
      self.displayname = displayname
      self.author = author
      self.url = url
      self.secret = secret
    
      if exits is None:
        exits = []
      if items is None:
        items = []
      if keys is None:
        keys = []
        
        self.keys = keys
        self.items = items
        self.exits = exits

def destinations_embed(self, adventure_rooms, player):
  exits = 0
  view = discord.ui.View()
  inventory = player["inventory"]
  journal = player["journal"]
  for room_id in self.exits:
    found_room = database.rooms.find_one({"id": room_id})
    if found_room:
      exits += 1