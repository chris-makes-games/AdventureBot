#used to parse user input and truncate if too long
#called by any commands which gets user input

import database

id_min = 6
id_max = 20
adventure_max = 100
desc_max = 2000
display_max = 100
entrance_max = 50
condition_max = 20

#used for all truncations except ID
def truncator(string, max):
    warning = False
    if len(string) > max:
        warning = True
        string = string[:max]
    return string, warning

#id separate, because there's also a minimum
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

def adventure(adventure):
    warning = None
    string, warn = truncator(adventure, adventure_max)
    if warn:
        warning = f"Your adventure name was too long! {adventure_max} characters max. The description was reduced to only the first {adventure_max} characters."
    return string, warning

def description(desc):
    warning = None
    string, warn = truncator(desc, desc_max)
    if warn:
        warning = f"Your description was too long! {desc_max} characters max. The description was reduced to only the first {desc_max} characters."
    return string, warning

def display(display):
    warning = None
    string, warn = truncator(display, display_max)
    if warn:
        warning = f"Your displayname was too long! {display_max} characters max. The description was reduced to only the first {display_max} characters."
    return string, warning

def entrance(entrance):
    warning = None
    string, warn = truncator(entrance, entrance_max)
    if warn:
        warning = f"Your entrance was too long! {entrance_max} characters max. The description was reduced to only the first {entrance_max} characters."
    return string, warning
    

