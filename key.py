import database


class Key:
  def __init__(self, id=None,
    displayname="", subkeys=None, author=None, 
    description="", item=False, journal=False,
    infinite=False):
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
      self.author = author
      self.displayname = displayname
      self.description = description
      self.infinite = infinite

      if subkeys is None:
        self.subitems = []
      self.subkeys = subkeys