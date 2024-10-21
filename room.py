import database


class Room:
  def __init__(
    self, id="", displayname="", description="", entrance="",
    author="", url="", alt_entrance="", deathnote="", adventure="",
    end=False, once=False, hidden=False, locked=False, 
    keys=None, destroy=None, exits=None, 
    unlock=None, reveal=None, hide=None, lock=None):
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
    #boolean attributes
    self.end = end
    self.once = once
    self.hidden = hidden
    self.locked = locked
    #dicts
    if keys is None:
        keys = {}
    if destroy is None:
        destroy = {}
    if lock is None:
        lock = {}
    if unlock is None:
        unlock = {}
    if hide is None:
        hide = {}
    if reveal is None:
        reveal = {}
    self.keys = keys
    self.destroy = destroy
    self.lock = lock
    self.unlock = unlock
    self.hide = hide
    self.reveal = reveal
    #exits still a list of strings
    if exits is None:
        exits = []
    self.exits = exits