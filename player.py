class Player:
  def __init__(self, discord, displayname, room, guilds=None,  game_threads=None, edit_thread=None,
               alive=True, deaths=0, architect=False, inventory=None, taken=None):
    self.disc = discord
    self.displayname = displayname
    self.alive = alive
    self.deaths = deaths
    self.room = room
    self.architect = architect
    self.edit_thread_id = edit_thread
    if inventory is None:
      inventory = []
    if taken is None:
      taken = []
    if guilds is None:
      guilds = []
    if game_threads is None:
      game_threads = []
    self.inventory = inventory
    self.taken = taken
    self.guilds = guilds
    self.game_threads = game_threads