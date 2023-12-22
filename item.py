import database

class Item:
    def __init__(self, 
          id="", displayname="", subitems=None, 
          description="", event_marker=False, 
          infinite=False, deconstructable=False, dict=None):

      if dict is not None:
        self.id = database.generate_unique_id()
        for key, value in dict.items():
            setattr(self, key, value)
      if self.displayname == "":
        self.displayname = "NO DISPLAY NAME GIVEN"
      if self.description == "":
        self.description = "NO DESCRIPTION GIVEN"
      self.event_marker = event_marker
      if subitems is None:
        subitems = []
      self.subitems = subitems
      self.infinite = infinite
      self.deconstructable = deconstructable