import database


class Room:
  def __init__(
    self, id="", displayname="", description="", entrance="",
    author="", url="", alt_entrance="", deathnote="", adventure="",
    end=False, once=False, hidden=False, locked=False, 
    keys=None, destroy=None, exits=None, 
    unlock="", reveal="", hide="", lock=""):
    #generates new id if none is given
    if not id:
      self.id = database.generate_unique_id()
    else:
      self.id = id
    #string attributes
    self.displayname = displayname
    self.description = description
    self.entrance= entrance
    self.alt_entrance = alt_entrance
    self.deathnote = deathnote
    self.author = author
    self.url = url
    self.adventure = adventure
    #string attributes that used to be lists
    self.unlock = unlock
    self.reveal = reveal
    self.hide = hide
    self.lock = lock
    #boolean attributes
    self.end = end
    self.once = once
    self.hidden = hidden
    self.locked = locked
    
    #keys is now a dict
    #key_id, number_of_keys
    if keys is None:
        keys = {}
    #destroy is also dict
    if destroy is None:
        destroy = {}
    #exits still a list of strings
    if exits is None:
        exits = []
    self.keys = keys
    self.destroy = destroy
    self.exits = exits