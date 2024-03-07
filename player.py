class Player:
  def __init__(self, discord, displayname, room,  guild_thread=None, edit_thread=None,
               alive=True, deaths=0, architect=False, inventory=None, taken=None):
    self.disc = discord
    self.displayname = displayname
    self.alive = alive
    self.deaths = deaths
    self.room = room
    self.architect = architect
    self.edit_thread = edit_thread
    self.guild_thread = guild_thread
    if inventory is None:
      inventory = []
    if taken is None:
      taken = []
    self.inventory = inventory
    self.taken = taken