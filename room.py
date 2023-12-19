class Room:
  def __init__(self, 
               name, displayname, author, 
               description="", 
               kill=False, exits=None, items=None, 
               exit_destination=None, 
               secrets=None, unlockers=None, url=""):
    
    self.name = name
    self.description = description
    self.kill = kill
    self.displayname = displayname
    self.author = author
    self.url = url
    
    if exits is None:
      exits = []
    self.exits = exits
    if items is None:
      items = []
    self.items = items
    if exit_destination is None:
      exit_destination = []
    self.exit_destination = exit_destination
    if secrets is None:
      secrets = []
    self.secrets = secrets
    if unlockers is None:
      unlockers = []
      self.unlockers = unlockers