import database


class Key:
  def __init__(self, id=None,
    displayname=None, subkeys=None, author=None, note=None, alt_note=None, description=None, 
combine = False, inventory=False, journal=False deconstruct=False, unique=False, repeating=False, stackable=False):
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
    self.combine = combine
    self.deconstruct = deconstruct
    self.unique = unique
    self.repeating = repeating
    self.stackable = stackable
    self.inventory = inventory
    self.journal = journal

    #subkeys now a dict
    if subkeys is None:
      self.subkeys = {}
    self.subkeys = subkeys