class Adventure:
  def __init__(self, name, start, author, description, rooms=None, epilogue=False, ready=False, total_plays=0):
      self.name = name
      self.start = start
      self.author = author
      self.description = description
      self.epilogue = epilogue
      self.ready = ready
      if rooms is None:
          rooms = []
      self.rooms = rooms
      self.total_plays = total_plays

  def add_room(self, room):
      self.rooms.append(room)
