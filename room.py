import database


class Room:
    def __init__(
        self, id="", displayname="", description="", entrance="",
        author="", url="", alt_entrance="", deathnote="", adventure="",
        end=False, once=False, hidden=False, locked=False, 
        keys=None, destroy=None, 
        exits=None, lock=None, unlock=None, hide=None, reveal=None):
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
        #dicts for key comprehension with keyID : amount format
        if keys is None:
            keys = {}
        if destroy is None:
            destroy = {}
        self.keys = keys
        self.destroy = destroy
        #lists of strings for exits and conditionals
        if exits is None:
            exits = []
        if lock is None:
            lock = []
        if unlock is None:
            unlock = []
        if hide is None:
            hide = []
        if reveal is None:
            reveal = []
        self.exits = exits
        self.lock = lock
        self.unlock = unlock
        self.hide = hide
        self.reveal = reveal

    #Creates a Room instance from a dictionary, using default values for missing fields.
    @classmethod
    def from_dict(cls, room_dict):
        #dictionary for expected/default variable types for attributes
        expected_attributes = {
            "id": (str, ""),
            "displayname": (str, ""),
            "description": (str, ""),
            "entrance": (str, ""),
            "alt_entrance": (str, ""),
            "deathnote": (str, ""),
            "author": (str, ""),
            "url": (str, ""),
            "adventure": (str, ""),
            "end": (bool, False),
            "once": (bool, False),
            "hidden": (bool, False),
            "locked": (bool, False),
            "keys": (dict, {}),
            "destroy": (dict, {}),
            "exits": (list, []),
            "lock": (list, []),
            "unlock": (list, []),
            "hide": (list, []),
            "reveal": (list, [])
        }
        #dict for fixing any bad attributes
        corrected_attributes = {}

        #fix all attributes if necessary
        for attr, (expected_type, default_value) in expected_attributes.items():
            value = room_dict.get(attr, default_value)
            if not isinstance(value, expected_type):
                if expected_type == list:
                    corrected_attributes[attr] = list(value) if isinstance(value, (set, tuple, dict)) else default_value
                elif expected_type == dict:
                    corrected_attributes[attr] = dict(value) if isinstance(value, (list, set, tuple)) else default_value
                else:
                    corrected_attributes[attr] = expected_type(value) if value else default_value
            else:
                corrected_attributes[attr] = value
        return cls(**corrected_attributes)
