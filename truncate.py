#used to parse user input and truncate if too long

import yaml
import database

#YAML config file for character limits
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    char_limits = config["EmbedLimits"]
    id_min = char_limits["id_min"]
    id_max = char_limits["id_max"]
    desc_max = char_limits["description"]
    display_max = char_limits["display"]
    entrance_max = char_limits["entrance"]
    condition_max = char_limits["condition"]

def id(id):
    warning = None
    if len(id) < id_min:
        id = database.generate_unique_id()
        warning = "ID was shorter than 6 characters! A random ID was generated instead."
        return id, warning
    elif len(id) > id_max:
        id = id[:20]
        warning = "ID was longer than 20 characters! Using the first 20..."
        return id, warning
    else:
        return id, warning

def description(desc):
    warning = None
    if len(desc) > desc_max:
        pass

