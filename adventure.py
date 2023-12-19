import database

class Adventure:
  def __init__(self, name, start, author, description):
      self.name = name
      self.start = start
      self.author = author
      self.description = description
      self.tree = []
      self.room_tree = []
      
  def build_room_tree(self, room_name, visited=None, depth=0):
    if visited is None:
      visited = set()
    if room_name in visited:
    # Room has already been visited, skip processing to break the loop
      return
    visited.add(room_name)
    room_branch = [room_name, []]
    root_room = database.get_room(room_name)
    if root_room:
        for exit in root_room["exit_destination"]:
          if exit not in self.tree:
            self.tree[1].append(self.build_room_tree(exit, visited))
            #self.tree.append("    " * depth + exit)
            #depth += 1


  


