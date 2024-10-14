class Player:
  def __init__(self, discord, displayname, room, guild, owned_adventures=None, coauthor=None, play_thread=None, keys=None, alive=True, deaths=0, architect=False, history=None):
    self.disc = discord #their discord name
    self.displayname = displayname #their displayname in the server they became a player
    self.alive = alive #bool if they are alive
    self.deaths = deaths #number of deaths they have died
    self.room = room #their current room
    self.architect = architect #bool if they are an architect, used for architect commands
    self.guild = guild #the server ID where they were created as a player
    self.play_thread = play_thread #thread ID where they are currently playing
    
    #empty defaults turn to empty lists/dicts
    if history is None:
      history = []
    if keys is None:
      keys = {}
    if owned_adventures is None:
      owned_adventures = []
    if coauthor is None:
      coauthor = []
      
    self.owned_adventures = owned_adventures #list of adventures they own by adventure name. Usually just 1
    self.coauthor = coauthor #list of adventures they are allowed to meddle with by adventure name
    self.history = history #list of rooms they've been in and item's they have collected
    self.keys = keys #dict of keys they have in the format {ID : amount}
    