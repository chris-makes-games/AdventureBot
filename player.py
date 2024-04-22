class Player:
  def __init__(self, discord, displayname, room, guild_thread=None, edit_thread=None, journal=None, keys=None, alive=True, deaths=0, architect=False, inventory=None, history=None):
    self.disc = discord
    self.displayname = displayname
    self.alive = alive
    self.deaths = deaths
    self.room = room
    self.architect = architect
    self.guild_thread = guild_thread
    if inventory is None:
      inventory = []
    if history is None:
      history = []
    if journal is None:
      journal = []
    if keys is None:
      keys = {}
    if edit_thread is None:
      edit_thread = []
    self.inventory = inventory
    self.history = history
    self.journal = journal
    self.keys = keys
    self.edit_thread = edit_thread
    