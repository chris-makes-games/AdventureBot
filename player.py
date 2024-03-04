class Player:
  def __init__(self, discord, displayname, room,  guilds_threads=None, edit_thread=None,
               alive=True, deaths=0, architect=False, inventory=None, taken=None):
    self.disc = discord
    self.displayname = displayname
    self.alive = alive
    self.deaths = deaths
    self.room = room
    self.architect = architect
    self.edit_thread = edit_thread
    if inventory is None:
      inventory = []
    if taken is None:
      taken = []
    if guilds_threads is None:
      guilds_threads = []
    self.inventory = inventory
    self.taken = taken
    self.guilds_threads = guilds_threads