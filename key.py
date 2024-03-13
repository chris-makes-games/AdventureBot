import database


class Key:
  def __init__(self, id=None,
    displayname="", subkeys=None, author=None, 
    description="", inventory=False, journal=False, alt_description=None,
    unique=False, repeating=False, stackable=False):
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
    #string attributes
    self.author = author
    self.displayname = displayname
    self.description = description
    self.alt_description = alt_description

    #boolean attributes
    self.inventory = inventory
    self.journal = journal
    self.unique = unique
    self.repeating = repeating
    self.stackable = stackable

    #list attributes
    if subkeys is None:
      self.subkeys = []
    self.subkeys = subkeys