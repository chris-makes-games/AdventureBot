class Player:
  def __init__(self, discord, displayname, room, channel, current_adventure=None, game_thread_id="", edit_thread_id="",
               alive=True, deaths=0, architect=False,
              inventory=None, taken=None):
    self.disc = discord
    self.displayname = displayname
    self.alive = alive
    self.deaths = deaths
    self.current_adventure = current_adventure
    self.room = room
    self.architect = architect
    self.channel = channel
    self.game_thread_id = game_thread_id
    self.edit_thread_id = edit_thread_id
    if inventory is None:
      inventory = []
    if taken is None:
      taken = []
    self.taken = taken
    self.inventory = inventory