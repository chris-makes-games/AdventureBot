
class Adventure:
  def __init__(self, nameid, start, author, description, rooms=None, epilogue=False):
      self.nameid = nameid
      self.start = start
      self.author = author
      self.description = description
      self.epilogue = epilogue
      self.tree = []
      self.room_tree = []
      if rooms is None:
          rooms = []
      self.rooms = rooms
