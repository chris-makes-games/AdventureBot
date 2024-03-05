import os  #used to store secrets
import pathlib  #to get commands from command folder
import re  #for regex autocompletion
from collections import Counter  #list comparing tool

import discord  #all bot functionality
from discord import app_commands  #slash commands
from discord.ext import commands  #commands for bot

import database  #mongodb database
import formatter  #formats embeds
import mapper  #for ascii map
from player import Player  #player class
from room import Room  #room class

#token for use with discord API
my_secret = os.environ['TOKEN']

#intents rescricts scope of discord bot
intents = discord.Intents().all()

#the channel ID needs to be in this list
#bot ignores all other channels
protectedchannels = [
  770017224844116031,
  1180274480807956631,
  1180315816294625291,
  1186398826148417707,
  1186464529366921286,
  908522799772102739,
  1183954110513414164,
  1187417491576729620,
  1192186126623064084
]

#bot will be the async client for running commands
#remove help to replace with my own
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

#guild IDs that the bot is in, for now
guild_ids = [730468423586414624]

#sets the parent directory of the bot
BASE_DIR = pathlib.Path(__file__).parent
#this is the command folder directory
#commands are stored in this folder
CMDS_DIR = BASE_DIR / "cmds"

#previous commands moved to folder
#previous commands moved to folder
#previous commands moved to folder
#previous commands moved to folder
#previous commands moved to folder
#previous commands moved to folder
#(this used to be where slash commands started)

@bot.tree.command(name="editadventure", description="Edit adventure properties")
@app_commands.choices(field=[
  app_commands.Choice(name="Name", value="nameid"),
  app_commands.Choice(name="Starting Room", value="start"),
  app_commands.Choice(name="Description", value="description")])

async def editadventure(interaction: discord.Interaction, nameid: str, field: app_commands.Choice[str], value: str):
  # Retrieve adventure and verify author
  adventure = database.testadventures.find_one({"nameid": nameid})
  if not adventure:
    await interaction.response.send_message("Error: Adventure not found! Double check your adventure ID!", ephemeral=True)
    return
  if interaction.user.id == adventure.get("author"):
    confirm = database.confirm_embed(confirm_text=f"This will edit the {field.name} to '{value}'", title="Confirm Adventure Edit", action="edit_adventure", channel=interaction.channel, id=nameid)
    await interaction.response.send_message(confirm)
    return
  else:
    await interaction.response.send_message("You do not have permission to edit this adventure.", ephemeral=True)
    return

# Autocompletion for nameid parameter in editadventure
@editadventure.autocomplete('nameid')
async def autocomplete_adventure_nameid(interaction: discord.Interaction, current: str):
  # Query the database for adventure nameids, filtering by author and nameid
  adventures_query = database.testadventures.find(
  {
  "author": interaction.user.id, 
  "nameid": {"$regex": re.escape(current), "$options": "i"}
  },
  {
  "nameid": 1,
  "_id": 0
  }
  )
  # Fetch up to 25 item IDs for the autocomplete suggestions
  adventure_ids = [adventure["nameid"] for adventure in adventures_query.limit(25)]
  # Create choices for each suggestion
  return [app_commands.Choice(name=nameid, value=nameid) for nameid in adventure_ids]

@bot.tree.command(name="edititem", description="Edit item properties")
@app_commands.describe(itemid="The ID of the item to edit", field="The property to edit", value="The new value for the property")
@app_commands.choices(field=[
    # Assuming these are the fields for the items you can edit
    app_commands.Choice(name="displayname", value="displayname"),
    app_commands.Choice(name="description", value="description"),
    # Add more fields here as necessary...
])
async def edititem(interaction: discord.Interaction, itemid: str, field: app_commands.Choice[str], value: str):
    # Retrieve item information from the database
    item = database.testitems.find_one({"itemid": itemid})
    if item:
        # Check if the author's ID (assuming an 'author' field exists in your item schema) matches the one stored in the database
        if interaction.user.id == item.get("author"):
            # Update information in the database
            match field.value:
                case "displayname":
                    val = value
                case "description":
                    val = value

                # Add more cases here as necessary...
                case _:
                    await interaction.response.send_message("Invalid field.")
                    return
            result = database.testitems.find_one_and_update(
                {"itemid": itemid},
                {"$set": {field.value: val}},
                return_document=True
            )
            if result:
                # Display the updated item information
                embed = discord.Embed(title=f"Item '{result.get('displayname', 'Unnamed Item')}'", description="The item has been updated.", color=0x00ff00)
                # Add all relevant fields to display
                fields_to_display = ["displayname", "description"]  # Add more as necessary...
                for field_name in fields_to_display:
                    embed.add_field(name=field_name, value=str(result.get(field_name, "Not Available")), inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Item not found in the database.")
        else:
            await interaction.response.send_message("You don't have permission to edit this item.")
    else:
        await interaction.response.send_message("Item not found in the database.")
# Autocompletion for itemid parameter
@edititem.autocomplete('itemid')
async def autocomplete_itemid(interaction: discord.Interaction, current: str):
    # Modify the query to also return the displayname field
    item_ids_query = database.testitems.find(
        {"author": interaction.user.id, "itemid": {"$regex": re.escape(current), "$options": "i"}},
        {"itemid": 1, "displayname": 1, "_id": 0}
    )
    # Create a list of tuples where each tuple contains the item ID and display name
    item_ids = [(item["itemid"], item["displayname"]) for item in item_ids_query]
    # Create a list of choices where each choice has the item ID as the value and the display name as the name
    return [app_commands.Choice(name=f"{item_id} - {displayname}", value=item_id) for item_id, displayname in item_ids[:25]]

@bot.tree.command(name="editroom", description="Edit room properties")
@app_commands.describe(roomid="The ID of the room to edit", field="The property to edit", value="The new value for the property")
@app_commands.choices(field=[
    app_commands.Choice(name="displayname", value="displayname"),
    app_commands.Choice(name="description", value="description"),
    app_commands.Choice(name="kill", value="kill"),
    app_commands.Choice(name="URL", value="URL"),
    app_commands.Choice(name="items", value="items"),
])
async def editroom(interaction: discord.Interaction, roomid: str, field: app_commands.Choice[str], value: str):
        # Retrieve information from the database
        result = database.testrooms.find_one({"roomid": roomid})
        if result:
            # Check if the author's ID matches the one stored in the database
            if interaction.user.id == result.get("author"):
                # Update information in the database
                match field.value:
                    case "description":
                        val = value
                    case "kill":
                        val = value.lower() == "true"
                    case "displayname":
                        val = value
                    case "URL":
                        val = value
                    case "items":
                        val = value
                    case _:
                        await interaction.response.send_message("Invalid field.")
                        return
                result = database.testrooms.find_one_and_update(
                    {"roomid": roomid},
                    {"$set": {field.value: val}},
                    return_document=True
                )
                if result:
                    # Display the updated room information
                    embed = discord.Embed(title=result["roomid"], description="Here you can see the updates to this room.", color=0x00ff00)
                    fields_to_display = ["displayname", "description", "kill", "URL", "items"]
                    for field_display in fields_to_display:
                        embed.add_field(name=field_display, value=result.get(field_display, "Not Available"), inline=False)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Room not found in the database.")
            else:
                await interaction.response.send_message("You don't have permission to edit this room.")
        else:
            await interaction.response.send_message("Room not found in the database.")
# Autocompletion for roomid parameter
@editroom.autocomplete('roomid')
async def autocomplete_roomid(interaction: discord.Interaction, current: str):
    # Modify the query to also return the displayname field
    room_ids_query = database.testrooms.find(
        {"author": interaction.user.id, "roomid": {"$regex": re.escape(current), "$options": "i"}},
        {"roomid": 1, "displayname": 1, "_id": 0}
    )
    # Create a list of tuples where each tuple contains the room ID and display name
    room_ids = [(room["roomid"], room["displayname"]) for room in room_ids_query]
    # Create a list of choices where each choice has the room ID as the value and the display name as the name
    return [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_ids[:25]]

@bot.tree.command(name="editroomarrays", description="Edit array fields of a room")
@app_commands.choices(field=[
    app_commands.Choice(name="exits", value="exits"),
    app_commands.Choice(name="exit_destination", value="exit_destination"),
    app_commands.Choice(name="secrets", value="secrets"),
    app_commands.Choice(name="unlockers", value="unlockers"),
])
async def editroomarrays(interaction: discord.Interaction, roomid: str, field: str, values: str):
          # Split the incoming values by comma to create a list of strings
          values_list = values.split(",")
          # Validation of input parameters
          if not roomid or not field or not values_list:
              await interaction.response.send_message("Invalid input parameters.")
              return
          # Process updates for a single array field
          array_fields = ["exits", "exit_destination", "secrets", "unlockers"]
          if field.lower() in array_fields:
              # Update information in the database
              result = database.testrooms.find_one_and_update(
                  {"roomid": roomid},
                  {"$set": {field.lower(): values_list}},  # Changed from $push to $set for overwriting the list
                  return_document=True
              )
              if result:
                  # Display the updated room information for the array field
                  embed = discord.Embed(title=result["roomid"], description="Here you can see the updates to this room.", color=0x00ff00)
                  embed.add_field(name=field, value="\n".join(result.get(field.lower(), [])), inline=True)
                  await interaction.response.send_message(embed=embed)
              else:
                  await interaction.response.send_message("Room not found in the database.")
          else:
              await interaction.response.send_message("Invalid array field. Supported fields: exits, exit_destination, secrets, unlockers")

# Autocompletion for roomid parameter in editroomarrays
@editroomarrays.autocomplete('roomid')
async def autocomplete_roomid_arrays(interaction: discord.Interaction, current: str):
    # Modify the query to also return the displayname field
    room_ids_query = database.testrooms.find(
        {"author": interaction.user.id, "roomid": {"$regex": re.escape(current), "$options": "i"}},
        {"roomid": 1, "displayname": 1, "_id": 0}
    )
    # Create a list of tuples where each tuple contains the room ID and display name
    room_ids = [(room["roomid"], room["displayname"]) for room in room_ids_query]
    # Create a list of choices where each choice has the room ID as the value and the display name as the name
    return [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_ids[:25]]

@bot.tree.command(name="exampleroom", description="Show an example room")
async def exampleroom(interaction: discord.Interaction, roomid: str):
  # Retrieve information from the database
  result = database.testrooms.find_one({"roomid": roomid })
  if result:
    embed = discord.Embed(title=result["roomid"], description="this is the example.", color=0x00ff00)
    fields = ["displayname", "description", "kill","URL", "items"]
    arrayfields = ["exits", "exit_destination"] 
    arrayfieldss = ["secrets", "unlockers"]
    for field in fields: 
      embed.add_field(name= field, value=result[field], inline=False)
    for field in arrayfields: 
      embed.add_field(name= field, value="\n".join(result[field]), inline=True)
    for field in arrayfieldss: 
      embed.add_field(name= field, value="\n".join(result[field]), inline=True)
    await interaction.response.send_message(embed=embed)
    followup_message = "**/exampleroom**  **exampleroom1** to see a reference on what each section of the room is for. **/exampleroom**  **exampleroom2** to see a reference on what the code will look like when updating the fields that are strings( roomid displayname description kill URL item ). **/exampleroom** **exampleroom3** to see how to update the arrays( exits exit_destination secrets unlockers) Use **/exampleroom** + **exampleroom4** to see the last master example room. To view any of the rooms shown in the Example Adventure, Simply use the roomid as follows **/exampleroom**  **roomid**.\nAlso you should /join the **Example Adventure** to see step by step visuals on how to edit rooms. This will also show you the players perspective when they play your adventure you are creating."
    await interaction.followup.send(followup_message)
  else:
    await interaction.response.send_message("Room not found in the database.")

# Autocompletion function for roomid in exampleroom command
@exampleroom.autocomplete('roomid')
async def autocomplete_exampleroom(interaction: discord.Interaction, current: str):
    # Modify the query to also return the displayname field
    example_room_ids_query = database.testrooms.find(
        {},
        {"roomid": 1, "displayname": 1, "_id": 0}
    )
    # Create a list of tuples where each tuple contains the room ID and display name
    example_room_ids = [(room["roomid"], room["displayname"]) for room in example_room_ids_query]
    # Filter the room IDs based on the current input
    filtered_room_ids = [(roomid, displayname) for roomid, displayname in example_room_ids if current.lower() in roomid.lower()]
    # Create a list of choices where each choice has the room ID as the value and the display name as the name
    return [app_commands.Choice(name=f"{roomid} - {displayname}", value=roomid) for roomid, displayname in filtered_room_ids[:25]]


@bot.tree.command(name="getroom", description="recall a room for viewing")
async def getroom(interaction: discord.Interaction, roomid: str):
  # Retrieve information from the database
  result = database.testrooms.find_one({"roomid": roomid })
  if result:
    # Check if the author's ID matches the one stored in the database
    if interaction.user.id == result.get("author"):
      embed = discord.Embed(title=result["roomid"], description="Here is your room. Please use the command **/exampleroom**  **exampleroom1** to see an example on how to update the room correctly. /join the **Example Adventure** as a player as well. The command to edit your room is **/editroom**  **(roomid)**  **(Field you are editing)** **(new information)**", color=0x00ff00)
      fields = ["displayname", "description", "kill", "url", "items"]
      arrayfields = ["exits", "exit_destination"] 
      arrayfieldss = ["secrets", "unlockers"]
      for field in fields: 
        embed.add_field(name=field, value=result[field], inline=False)
      for field in arrayfields: 
        embed.add_field(name=field, value="\n".join(result[field]), inline=True)
        embed.add_field(name="", value="", inline=False)
      for field in arrayfieldss: 
        embed.add_field(name=field, value="\n".join(result[field]), inline=True)
      await interaction.response.send_message(embed=embed)
    else:
      await interaction.response.send_message("You don't have permission to view this room.")
  else:
    await interaction.response.send_message("Room not found in the database.")

# Autocompletion for roomid parameter in getroom
@getroom.autocomplete('roomid')
async def autocomplete_getroom(interaction: discord.Interaction, current: str):
      # Query the database for room IDs created by the user, using regex for filtering based on the current input
      room_ids_query = database.testrooms.find(
    {"author": interaction.user.id, "roomid": {"$regex": re.escape(current), "$options": "i"}},
    {"roomid": 1, "displayname": 1, "_id": 0})
  # Create a list of tuples where each tuple contains the room ID and display name
      room_ids = [(room["roomid"], room["displayname"]) for room in room_ids_query]
      return [app_commands.Choice(name=f"{rid} - {displayname}", value=rid) for rid, displayname in room_ids[:25]]


#Makes a new room in the database
@bot.tree.command(name= "newroom", description= "Create a new room")
async def newroom(interaction: discord.Interaction):
    truename = interaction.user.id
    name = interaction.user.display_name  # Define the 'name' variable within the 'newroom' command
    try:
        database.create_blank_room(truename)
        embed = formatter.blank_embed(name, "Success", "Room was created, use the get room command /getroom  to view the room you just made.", "green")
    except Exception as e:
        embed = formatter.blank_embed(name, "Error", str(e), "red")
    await interaction.response.send_message(embed=embed)

#Makes a new blank item in the database
@bot.tree.command(name= "newitem", description= "Create a new item")
async def newitem(interaction: discord.Interaction):
      author_id = interaction.user.id  # capture the user ID of the person interacting
      name = interaction.user.display_name
      try:
        database.create_blank_item(author_id)  # pass the user ID to create_blank_item
        embed = formatter.blank_embed(name, "Success", "Item was created", "green")
      except Exception as e:
        embed = formatter.blank_embed(name, "Error", str(e), "red")
      await interaction.response.send_message(embed=embed)

#makes a new adventure in the database
@bot.tree.command(name="newadventure", description="Create a new adventure")
async def newadventure(interaction: discord.Interaction):
    truename = interaction.user.id
    name = interaction.user.display_name
    channel = interaction.channel
    # Check if the author already has an adventure
    if database.testadventures.find_one({"author": truename}):
        embed = formatter.blank_embed(name, "Error", "You already have an existing adventure. You cannot create more than one.", "red")
        await interaction.response.send_message(embed=embed)
        return
    # Check for existing edit thread
    player = database.get_player(truename)
    if player and player["edit_thread"]:
        embed = formatter.blank_embed(name, "Error", "You already have an existing thread for editing adventures. Please use that for editing your adventure.", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    # Check for the player existing in the database
    elif not player:
        embed = formatter.blank_embed(name, "Error", "You are not a player. Please use /join Example Adventure to begin", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    # Checks for the player having joined the example adventure
    # elif player["current_adventure"] != "example adventure":
    #     embed = formatter.blank_embed(name, "Error", "You are not in the Example Adventure. Please use /join Example Adventure to begin", "red")
    #     await interaction.response.send_message(embed=embed, ephemeral=True)
    #     return
    else:
        # Create the adventure first
        database.create_blank_adventure(truename)
        # Then, create a new thread for editing this adventure
        database.pp("creating adventure edit channel:\n" + str(channel))
        if channel and channel.type == discord.ChannelType.text:
          thread = await channel.create_thread(name=f"{name} editing an adventure")
          await thread.send(interaction.user.mention + " is editing an adventure.")
          edit_thread_id = channel.id
        # Update the player's editthread field with the new thread ID
          database.update_player({'disc': truename, 'edit_thread_id': edit_thread_id})
          embed = formatter.blank_embed(name, "Success", f"Adventure was created and your edit thread is ready! Thread ID: {edit_thread_id}", "green")
          await interaction.response.send_message(embed=embed, ephemeral=True)

#returns a list of the truenames of items for the player
@bot.tree.command(name= "inventory", description= "View your inventory")
async def inventory(interaction: discord.Interaction):
    truename = interaction.user.id
    real_items = database.get_player_info(truename, "inventory")
    player = database.get_player(truename)
    embed = formatter.inventory(real_items)
    if player and player["alive"]:
      await interaction.response.send_message(embed=embed)
    else :
      await interaction.response.send_message("You are either dead or not in a adventure!")

#Lists the current adventures from the database
@bot.tree.command(name= "adventures", description= "A list of all playable adventures")
async def adventures(interaction: discord.Interaction):
  guild = interaction.guild
  adventures = database.get_adventures()
  adventure_names = []
  descriptions = []
  authors = []
  if guild is None:
    return
  for adventure in adventures:
    adventure_names.append(adventure["nameid"])
    descriptions.append(adventure["description"])
    author_id = adventure["author"]
    author = guild.get_member(author_id)
    if author:
      authors.append(author.display_name)
    else:
      authors.append("Unknown")
  embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use /join to start an adventure. More adventures will be available later!", color=0x00ff00)
  for i in range(len(adventure_names)):
    embed.add_field(name=adventure_names[i].title(), value=descriptions[i] + "\n*Created by: " + authors[i] + "*", inline=False)
  await interaction.response.send_message(embed=embed)
  return

#prints a connection message to the console for debugging
@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  #this should load all commands from commands folder
  for cmd_file in CMDS_DIR.glob("*.py"):
    try:
      if cmd_file.name != "__init__.py":
        if database.inactive_check(cmd_file.name[0:-3]):
          print(f"Skipping command: /{cmd_file.name[:-3]}...")
        else:
          print(f"Loading command: /{cmd_file.name[:-3]}...")
          await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")
    except Exception as e:
      print(f"Failed to load command: /{cmd_file.name[:-3]}")
      print(e)
  #this syncs the bot slash commands
  try: 
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} commands.')
  except Exception as e:
    print(e)

#prevents bot from answering its own messages
#requires messages stay in specific channels
#ignores messages that arent commands
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if not message.content.startswith("!"):
    return
  if message.channel.id in protectedchannels:
    await bot.process_commands(message)
  else:
    # makes sure that player can only respond to specific thread
    player_id = message.author.id
    player_channel_id = database.get_player_info(player_id, "channel")
    if message.channel.id != player_channel_id:
      return
    else:
      await bot.process_commands(message)

#runs the bot and throws generic errors
try:
  print("running")
  database.ping()
  bot.run(my_secret)
except Exception as e:
  print(e)
