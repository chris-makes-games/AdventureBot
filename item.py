import database


class Item:
    def __init__(self, itemid=None,
          displayname="", subitems=None, author=None, 
          description="", event_marker=False, 
          infinite=False, deconstructable=False, dict=None):

      if dict is not None:
        if not itemid:
          self.itemid = database.generate_unique_id()
        for key, value in dict.items():
            setattr(self, key, value)
        if self.displayname == "":
          self.displayname = "NO DISPLAY NAME GIVEN"
        if self.description == "":
          self.description = "NO DESCRIPTION GIVEN"
        if author is None:
          self.author = "INVALID AUTHOR"
      else:
        self.itemid = database.generate_unique_id()
        self.author = author
        self.displayname = displayname
        self.description = description
      
      self.infinite = infinite
      self.event_marker = event_marker
      self.deconstructable = deconstructable
      self.subitems = subitems
      if subitems is None:
        self.subitems = []