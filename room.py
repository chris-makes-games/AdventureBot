import database


class Room:
  def __init__(self, 
               roomid="", displayname="", author=None, 
               description="", 
               kill=False, exits=None, items=None, 
               exit_destination=None, 
               secrets=None, unlockers=None, url="", dict=None):
    if dict is not None:
      self.roomid = database.generate_unique_id()
      for key, value in dict.items():
          setattr(self, key, value)
      if self.description == "":
        self.description = "NO DESCRIPTION GIVEN"
      if self.displayname == "":
        self.displayname = "NO DISPLAY NAME GIVEN"
      if self.author == None:
        self.author = "INVALID AUTHOR"
    else:
      self.roomid = database.generate_unique_id()
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

  def generate_ascii_map(self, visited=None, indent=0):
    pass