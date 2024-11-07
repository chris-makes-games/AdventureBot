class Adventure:
    def __init__(self, name, start, author, description, rooms=None, epilogue=False, ready=False, coauthors=None, total_plays=0):
        self.name = name
        self.start = start
        self.author = author
        self.description = description
        self.epilogue = epilogue
        self.ready = ready
        if coauthors is None:
            coauthors = []
        if rooms is None:
            rooms = []
        self.rooms = rooms
        self.coauthors = coauthors
        self.total_plays = total_plays

    def add_room(self, room):
        self.rooms.append(room)
    
    #Creates an Adventure instance from a dictionary, using default values for missing fields.
    @classmethod
    def from_dict(cls, adventure_dict):
        #expected variable types for class attributes with defualt values
        expected_attributes = {
            "name": (str, ""),
            "start": (str, ""),
            "author": (str, ""),
            "description": (str, ""),
            "rooms": (list, []),
            "epilogue": (bool, False),
            "ready": (bool, False),
            "coauthors": (list, []),
            "total_plays": (int, 0)
        }

        #dict for corrected attributes as necessary
        corrected_attributes = {}

        #fixes all attribues, or assignes default values
        for attr, (expected_type, default_value) in expected_attributes.items():
            if attr not in expected_attributes:
                continue
            value = adventure_dict.get(attr, default_value)
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
