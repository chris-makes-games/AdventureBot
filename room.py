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
        return cls(
        id=room_dict.get("id", ""),
        displayname=room_dict.get("displayname", ""),
        description=room_dict.get("description", ""),
        entrance=room_dict.get("entrance", ""),
        author=room_dict.get("author", ""),
        url=room_dict.get("url", ""),
        alt_entrance=room_dict.get("alt_entrance", ""),
        deathnote=room_dict.get("deathnote", ""),
        adventure=room_dict.get("adventure", ""),
        end=room_dict.get("end", False),
        once=room_dict.get("once", False),
        hidden=room_dict.get("hidden", False),
        locked=room_dict.get("locked", False),
        keys=room_dict.get("keys", {}),
        destroy=room_dict.get("destroy", {}),
        exits=room_dict.get("exits", []),
        lock=room_dict.get("lock", []),
        unlock=room_dict.get("unlock", []),
        hide=room_dict.get("hide", []),
        reveal=room_dict.get("reveal", [])
        )
