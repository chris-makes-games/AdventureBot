import discord

import database


class Room:
  def __init__(
    self, id=None, displayname="", description="", entrance="",
    author="", url=None, alt_entrance="", deathnote=None,
    end=False, once=False, hidden=False, locked=False, 
    keys=None, exits=None, unlock=None, reveal=None, destroy=None, adventure=None,
    hide=None, lock=None):
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
    #list attributes
    if keys is None:
        keys = []
    if exits is None:
        exits = []
    if unlock is None:
        unlock = []
    if reveal is None:
        reveal = []
    if destroy is None:
        destroy = []
    if hide is None:
        hide = []
    if lock is None:
        lock = []
    self.keys = keys
    self.exits = exits
    self.unlock = unlock
    self.reveal = reveal
    self.destroy = destroy
    self.hide = hide
    self.lock = lock