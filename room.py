import database

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

  def generate_ascii_map(self, visited=None, indent=0):
    if visited is None:
        visited = set()

    if self.name in visited:
        return ""

    visited.add(self.name)

    result = " " * indent + f"{self.displayname} ({self.name})\n"

    for exit_name, destination_name in zip(self.exits, [self.exit_destination]):
        exit_room = database.get_room(destination_name)
        if exit_room:
            result += " " * (indent + 2) + f"{exit_name} -> {exit_room.displayname} ({destination_name})\n"
            result += exit_room.generate_ascii_map(visited, indent + 4)

    return result