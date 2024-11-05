import database

class Key:
  def __init__(self, id=None,
    displayname=None, adventure=None, subkeys=None, author=None, note=None, alt_note=None, description=None, 
    combine = False, inventory=False, journal=False, deconstruct=False, unique=False, repeating=False, stackable=False):
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
    #string attributes
    self.author = author
    self.adventure = adventure
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
  #Creates a Key instance from a dictionary, correcting types for all attributes as needed.
  @classmethod
  def from_dict(cls, key_dict):
    # Define expected types and default values for each attribute
    expected_attributes = {
      "id": (str, None),
      "displayname": (str, None),
      "subkeys": (dict, {}),
      "author": (int, 0),
      "adventure": (str, None),
      "note": (str, None),
      "alt_note": (str, None),
      "description": (str, None),
      "combine": (bool, False),
      "inventory": (bool, False),
      "journal": (bool, False),
      "deconstruct": (bool, False),
      "unique": (bool, False),
      "repeating": (bool, False),
      "stackable": (bool, False)
        }

    corrected_attributes = {}

    for attr, (expected_type, default_value) in expected_attributes.items():
      value = key_dict.get(attr, default_value)
      if not isinstance(value, expected_type):
        if expected_type == dict:
          corrected_attributes[attr] = dict(value) if isinstance(value, (list, set, tuple)) else default_value
        else:
          corrected_attributes[attr] = expected_type(value) if value else default_value
      else:
        corrected_attributes[attr] = value
    return cls(**corrected_attributes)