import database
import discord

class Room:
  def __init__(
    self, id=None, displayname="", description="", entrance="",
    author="", url="", alt_entrance="", deathnote="",
    end=False, once=False, hidden=False, locked=False, 
    keys=None, exits=None, unlock=None, reveal=None, destroy=None,
    hide=None, lock=None):
    #generates new id if none is given
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
    #string attributes
    self.displayname = displayname
    self.description = description
    self.entrance= entrance
    self.author = author #actually an int
    self.url = url
    #boolean attributes
    self.end = end
    self.once = once
    self.hidden = hidden
    self.locked = locked
    #list attributes
    if keys is None:
        keys = []
    if exits is None:
        exits = []
    if unlock is None:
        unlock = []
    if reveal is None:
        reveal = []
    if destroy is None:
        destroy = []
    if hide is None:
        hide = []
    if lock is None:
        lock = []
    self.keys = keys
    self.exits = exits
    self.unlock = unlock
    self.reveal = reveal
    self.destroy = destroy
    self.hide = hide
    self.lock = lock

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

#send an embed with buttons to go to different rooms
def destinations_embed(self, adventure_rooms, player):
  exits = 0
  view = discord.ui.View()
  inventory = player["inventory"]
  journal = player["journal"]
  for room_id in self.exits:
    found_room = database.rooms.find_one({"id": room_id})
    if found_room:
      exits += 1