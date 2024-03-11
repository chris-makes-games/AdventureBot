import database


class Key:
  def __init__(self, id=None,
    displayname="", subkeys=None, author=None, 
    description="", inventory=False, journal=False,
    unique=False, repeating=False, stackable=False):
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
    self.author = author
    self.displayname = displayname
    self.description = description
    self.unique = unique
    self.repeating = repeating

    if subkeys is None:
      self.subkeys = []
    self.subkeys = subkeys