class Item:
    def __init__(self, 
          name, displayname, subitems=None, 
          description="", 
          infinite=False, deconstructable=False):

      self.name = name
      self.displayname = displayname
      self.description = description
      if subitems is None:
        subitems = []
      self.subitems = subitems
      self.infinite = infinite
      self.deconstructable = deconstructable