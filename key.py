import database


class Key:
  def __init__(self, id=None,
    displayname=None, subkeys=None, author=None, note=None, alt_note=None, description=None, 
deconstruct=False, unique=False, repeating=False, stackable=False):
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
    #string attributes
    self.author = author
    self.displayname = displayname
    self.description = description
    self.note = note
    self.alt_note = alt_note

    #boolean attributes
    self.deconstruct = deconstruct
    self.unique = unique
    self.repeating = repeating
    self.stackable = stackable

    #list attributes
    if subkeys is None:
      self.subkeys = []
    self.subkeys = subkeys