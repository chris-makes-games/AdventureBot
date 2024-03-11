class Adventure:
  def __init__(self, name, start, author, description, rooms=None, epilogue=False, ready=False):
      self.name = name
      self.start = start
      self.author = author
      self.description = description
      self.epilogue = epilogue
      self.ready = ready
      if rooms is None:
          rooms = []
      self.rooms = rooms

  def add_room(self, room):
      self.rooms.append(room)
