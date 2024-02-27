import os  #used to store secrets
from collections import Counter  #list comparing tool

import re #for regex

import discord  #all bot functionality
from discord.ext import commands  #commands for bot
from discord import app_commands #slash commands

import database  #mongodb database
import formatter  #formats embeds
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

#simple ping command for testing
@bot.command()
async def ping(ctx):
  await ctx.reply('Pong!\n {0}'.format(round(bot.latency, 1)) + " seconds")

@bot.tree.command(name="load", description="loads a command")
async def load(ctx, command):
  print("loading " + str(command))
  await bot.reload_extension(f"commands.{command}")
  await ctx.reply("reloaded " + command)
  await bot.tree.sync()

@bot.tree.command(name="unload", description="unloads a command")
async def unload(ctx, command):
  print("unloading " + str(command))
  await bot.reload_extension(f"commands.{command}")
  await ctx.reply("unloaded " + command)
  await bot.tree.sync()

#deactivated valentines command, saving for later use just in case
# @bot.tree.command(name= "cupid", description= "Use this to submit your valentine for the event")
# async def cupid(interaction: discord.Interaction):
#   truename = interaction.user.id
#   tuple = await database.cupid_embed(truename)
#   embed = tuple[0]
#   view = tuple[1]
#   await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@bot.tree.command(name="register", description="Register a bot to a channel")
async def register(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    guild_id = interaction.guild_id
    if database.register_channel(channel_id, guild_id):
      await interaction.response.send_message("Bot has been registered to this channel.", ephemeral=True)
      print(f"Bot has been registered to channel: {channel_id}")
    else:
      await interaction.response.send_message("Failed to register the bot: guild already has a channel registered.", ephemeral=True)
      print("Error in register command: guild already has a channel in the database")

#generate unique ID and send for testing purposes
@bot.command()
async def randomid(ctx, *args):
  arg = int(''.join(args))
  await ctx.reply(database.generate_unique_id(arg))

@bot.command()
async def updaterooms(ctx):
  all_rooms = database.rooms.find()
  for room in all_rooms:
    room_object = Room(dict=room)
    room_id = room_object.roomid
    room_name = room_object.displayname
    print("checking room " + room_name)
    print("room ID: " + str(room_id))
    dict = room_object.__dict__
    database.update_room(dict)
    await ctx.send("room " + room_name + " updated with ID " + str(room_id) + " but still has a name")

#NUCLEAR DELETION OF ROOM FIELDS
#@bot.command()
#async def deleteroomfields(ctx, *args):
  #arg = ''.join(args)
  #database.delete_room_fields(arg)
  #await ctx.send(str(arg) + " removed from all rooms")

#old version, new version is handled by database
#injests items a room has, player inventory, player taken
#determines if the player needs to be given the item
#prevents duplicate items, returns a tuple
def give_player_items(new_items, old_items, taken):
  items_grouping = [new_items, old_items, taken]
  for item in new_items:
    item_object = None
    item_object = database.items.find_one({"name" : item})
    if not item_object:
      print("ERROR - Room item not found!")
      print(str(item) + " does not exist as an item name")
      continue
    elif item in old_items:
      new_items.remove(item)
      continue
    elif item in taken and not item_object["infinite"]:
      new_items.remove(item)
      continue
    elif item_object["infinite"] and item not in old_items:
      if item not in taken:
        taken.append(item)
      old_items.append(item)
    elif item not in old_items and item not in taken:
      taken.append(item)
      old_items.append(item)
    else:
      new_items.remove(item)
  database.pp("New Items:" + str(items_grouping))
  return items_grouping
  
#creates new players and adds them to the database
@bot.command()
async def join(ctx, *args):
  adventure_name = []
  truename = ctx.author.id
  name = ctx.author.display_name
  channel = ctx.channel
  if database.get_player(truename):
    embed = formatter.embed_message(name, "Error", "alreadyplayer" , "red")
    await ctx.reply(embed=embed)
    return
  for arg in args:
    adventure_name.append(str(arg))
  adventure_name = " ".join(adventure_name)
  all_adventures = database.get_adventures()
  if adventure_name == "":
    embed = discord.Embed(title="Error - Need adventure", description="You need to specify an adventure to join. Use !join <adventure name here>\nRefer to this list of available adventures:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  adventure = database.get_adventure(adventure_name.lower())
  if not adventure:
    embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please !join one of these adventures to begin:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  else:
    guild = ctx.guild
    thread = await channel.create_thread(name=name + "'s " + adventure_name)
    channel_id = thread.id
    player = Player(truename, name, adventure["start"], channel_id)
    database.new_player(player.__dict__)
    room = database.get_player_room(truename)
    if room is None:
      print("Error! Room is None!")
      embed = formatter.embed_message(name, "Error", "noroom", "red")
      await ctx.reply(embed=embed)
      return
    room_author = guild.get_member(room["author"])
    room_author_displayname = 'ERROR' if room_author is None else str(room_author.display_name)
    all_items = []
    new_items = []
    tuple = database.embed_room(all_items, new_items, room["displayname"], room)
    embed = tuple[0]
    view = tuple[1]
    embed.set_footer(text="This room was created by " + room_author_displayname)
    #un-comment to delete command after success
    #await ctx.message.delete()
    await thread.send(ctx.author.mention + "You have sucessfully begun an adventure. Use the buttons below to play. If you have questions, ask a moderator",embed=embed, view=view)

#creation mode for adding anything new or editing rooms
#edits one adventure at a time
#works similar to join, creates a private thread
@bot.command()
async def create(ctx, *args):
  adventure_name = []
  name = ctx.author.display_name
  channel = ctx.channel
  #delete comment to implememnt admin check
  #if player and not player["architect"]:
    #embed = formatter.embed_message(name, "Error", "notarchitect" , "red")
    #await ctx.reply(embed=embed)
    #return
  for arg in args:
    adventure_name.append(str(arg))
  adventure_name = " ".join(adventure_name)
  all_adventures = database.get_adventures()
  database.pp(all_adventures)
  if adventure_name == "":
    embed = discord.Embed(title="Error - Need adventure", description="You need to specify an adventure to begin creating. Use !create <adventure name here>\nRefer to this list of available adventures to edit:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  adventure = database.get_adventure(adventure_name.lower())
  if not adventure:
    embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please !create one of these adventures to begin creation mode:", color=discord.Color.red())
    for adventure in all_adventures:
      embed.add_field(name=adventure["nameid"].title(), value=adventure["description"], inline=False)
    embed.set_footer(text="If there is a different error, contact a moderator")
    await ctx.reply(embed=embed)
    return
  else:
    thread = await channel.create_thread(name=name + " editing " + adventure_name)
    channel = bot.get_channel(thread.id)
    tuple = await database.creation_mode(channel)
    embed = tuple[0]
    view = tuple[1]
    await ctx.message.delete()
    await thread.send(ctx.author.mention + "This is create mode",embed=embed, view=view)

#attempts to combine two items or more together
#soon to be removed, in favor of embed function
@bot.command()
async def combine(ctx, *args):
  truename = ctx.author.id
  inventory = database.get_player_info(truename, "inventory")
  name = ctx.author.display_name
  if len(args) < 2:
    embed = formatter.embed_message(name, "Error", "noitem", "red")
    await ctx.reply(embed=embed)
    return
  try:
    if inventory is None:
      embed = formatter.embed_message(name, "Error", "emptyinventory", "red")
      await ctx.reply(embed=embed)
      return
    for arg in args:
      if int(arg) > len(inventory):
        embed = formatter.embed_message(name, "Error", "noitem", "red")
        await ctx.reply(embed=embed)
        return
  except Exception as e:
    print(e)
    embed = formatter.embed_message(name, "Error", "noitem", "red")
    await ctx.reply(embed=embed)
    return
  combining_items = []
  for arg in args:
    combining_items.append(inventory[int(arg)-1])
  all_items = database.get_all_items()
  for item in all_items:
    if item["subitems"]:
      print("combining items...")
      print(item["subitems"])
      print(combining_items)
      if Counter(combining_items) == Counter(item["subitems"]):
        for olditem in combining_items:
          inventory.remove(olditem)
        inventory.append(item["itemid"])
        dict = {"disc": truename,"inventory": inventory}
        database.update_player(dict)
        embed = formatter.embed_message(name, "You created a " + item["displayname"] + "!", "combo", "green")
        await ctx.reply(embed=embed)
        return
  embed = formatter.embed_message(name, "Incorrect Combination", "nocombo", "red")
  await ctx.reply(embed=embed)
  return

#deconstructs an item, if such a thing is possible for that item
#soon to be removed, in favor of embed function
@bot.command()
async def deconstruct(ctx, item):
  truename = ctx.author.id
  inventory = database.get_player_info(truename, "inventory")
  name = ctx.author.display_name
  if inventory is None:
    embed = formatter.embed_message(name, "Error", "emptyinventory", "red")
    await ctx.reply(embed=embed)
    return
  try:
    trueitem = int(item)
    trueitem -= 1
    if int(item) > len(inventory):
      embed = formatter.embed_message(name, "Error", "noitem", "red")
      await ctx.reply(embed=embed)
      return
  except Exception as e:
    print(e)
    embed = formatter.embed_message(name, "Error", "noitem", "red")
    await ctx.reply(embed=embed)
    return
  scrap_item = inventory[trueitem]
  scrap_item = database.get_item(scrap_item)
  if scrap_item is None:
    embed = formatter.embed_message(name, "Error", "itemdoesntexist", "red")
    await ctx.reply(embed=embed)
    return
  new_items = scrap_item["subitems"]
  inventory.remove(scrap_item["name"])
  items_string = ""
  for item in new_items:
    inventory.append(item)
    itemname = database.get_item(item)
    if itemname:
      items_string = items_string + ("- " +itemname["displayname"] + "\n")
  dict = {"disc": truename,"inventory": inventory}
  database.update_player(dict)
  embed = formatter.blank_embed(name, "You deconstruct the " + scrap_item["displayname"], "after deconstruction the following items are added to your inventory:\n" + items_string, "green")
  await ctx.reply(embed=embed)
  return

#basic help command, replies with embed
#allows the user to optionally !help other commands
@bot.command()
async def help(ctx, *args):
  message = args[0] if len(args) > 0 else ""
  await ctx.reply(embed=formatter.help(message))

#Slash commands start here!!!!
#Slash commands start here!!!!
#Slash commands start here!!!!
#Slash commands start here!!!!
#Slash commands start here!!!!



class ConfirmKillButton(discord.ui.Button):
  def __init__(self, label, confirm, action, player_info, thread, style=discord.ButtonStyle.gray, disabled=False, row=0):
      custom_id = f'confirm_kill_{confirm}'  # Added custom_id for interaction handling
      super().__init__(label=label, style=style, disabled=disabled, row=row, custom_id=custom_id)
      self.confirm = confirm
      self.action = action
      self.player_info = player_info
      self.thread = thread
      if confirm:
          self.style = discord.ButtonStyle.green
      else:
          self.style = discord.ButtonStyle.red
  async def callback(self, interaction: discord.Interaction):
      if self.confirm:
          # Code to handle the player death
          database.kill_player(self.player_info['disc'])
          await self.thread.send(f"{self.player_info['displayname']} has died in the game.")
          # Fetch the channel from the bot's registration details in the database
          bot_info = database.botinfo.find_one({"name": self.player_info['bot_name']})
          if bot_info and 'channel' in bot_info:
              channel_id = bot_info['channel']
              channel = bot.get_channel(channel_id)
              if channel:
                  await channel.send(f"{self.player_info['displayname']} has died in the game.")
              else:
                  print(f"Channel with ID {channel_id} not found.")
          else:
              print(f"Bot info for {self.player_info['bot_name']} not found in database.")
          # Send a response back to the interaction
          await interaction.response.send_message(f"{self.player_info['displayname']} you have chosen another way out of the game, but you must still use the command /leave before starting another adventure.", ephemeral=True)
      else:
          await interaction.response.send_message("You have chosen to stay in the game.", ephemeral=False)



# In your kill command, you should display player stats and the confirmation button without deleting the player data upfront.
@bot.tree.command(name="kill", description="A way out of the game")
async def kill(interaction: discord.Interaction):
      truename = interaction.user.id
      player_info = database.get_player(truename)
      if not player_info:
          await interaction.response.send_message("You are not currently in a game.", ephemeral=True)
          return
      # Get the thread ID using the get_thread function
      thread_id = database.get_thread(truename)
      if not thread_id:
          await interaction.response.send_message("Game thread not found.", ephemeral=True)
          return
      # Verify that the command is used in the player's thread
      if interaction.channel_id != thread_id:
          await interaction.response.send_message("The /kill command can only be used in your game thread.", ephemeral=True)
          return

      thread = interaction.guild.get_thread(thread_id)
      if not thread:
          await interaction.response.send_message("Game thread not found or may have already been deleted.", ephemeral=True)
          return
      # Construct an embed with the confirmation
      embed = discord.Embed(title="Confirm Kill", description=f"Player: {player_info.get('displayname', 'Unknown')}\nAre you sure you want to do this?", color=discord.Color.red())
      # Create confirmation view with the 'leave_game' logic
      view = discord.ui.View()
      view.add_item(ConfirmKillButton(label="Yes", confirm=True, action="leave_game", player_info=player_info, thread=thread))
      view.add_item(ConfirmKillButton(label="No, stay in game", confirm=False, action="cancel", player_info=player_info, thread=thread))
      await interaction.response.send_message(embed=embed, view=view)






@bot.tree.command(name="join", description="Join an adventure")
async def join(interaction: discord.Interaction, adventure_name: str):
          truename = interaction.user.id
          name = interaction.user.display_name
          channel = interaction.channel
          command_channel = interaction.channel
          if database.get_player(truename):
            embed = formatter.embed_message(name, "Error", "alreadyplayer" , "red")
            await interaction.response.send_message(embed=embed)
            return
          all_adventures = database.get_adventures()
          if adventure_name == "":
            embed = discord.Embed(title="Error - Need adventure", description="You need to specify an adventure to join. Use /join <adventure name here>\nRefer to this list of available adventures:", color=discord.Color.red())
            for adventure in all_adventures:
              embed.add_field(name=adventure["name"].title(), value=adventure["description"], inline=False)
            embed.set_footer(text="If there is a different error, contact a moderator")
            await interaction.response.send_message(embed=embed)
            return
          adventure = database.get_adventure(adventure_name.lower())
          if not adventure:
            embed = discord.Embed(title="Error - No Such Adventure", description="Adventure '" + adventure_name + "' was not found. Please /join one of these adventures to begin:", color=discord.Color.red())
            for adventure in all_adventures:
              embed.add_field(name=adventure["name"].title(), value=adventure["description"], inline=False)
            embed.set_footer(text="If there is a different error, contact a moderator")
            await interaction.response.send_message(embed=embed)
            return
          else:
            guild = interaction.guild
            thread = await channel.create_thread(name=name + "'s " + adventure_name)
            channel_id = thread.id
            player = Player(truename, name, adventure["start"], channel_id, game_thread_id=thread.id)
            database.new_player(player.__dict__)
            room = database.get_player_room(truename)
            if room is None:
              print("Error! Room is None!")
              embed = formatter.embed_message(name, "Error", "noroom", "red")
              await interaction.response.send_message(embed=embed)
              return
            room_author = guild.get_member(room["author"])
            room_author_displayname = 'ERROR' if room_author is None else str(room_author.display_name)
            all_items = []
            new_items = []
            tuple = database.embed_room(all_items, new_items, room["displayname"], room)
            embed = tuple[0]
            view = tuple[1]
            embed.set_footer(text="This room was created by " + room_author_displayname)
            await thread.send(interaction.user.mention + "You have successfully begun an adventure. Use the buttons below to play. If you have questions, ask a moderator",embed=embed, view=view)
            await command_channel.send(interaction.user.mention + "You have successfully begun an adventure. If you have questions, ask a moderator")


# Autocompletion function for adventure_name in join command
@join.autocomplete('adventure_name')
async def autocomplete_adventure_name(interaction: discord.Interaction, current: str):
    # Query the database for adventure names and filter based on the current input
    adventures_query = database.get_adventures()
    possible_adventures = [adv["name"] for adv in adventures_query if current.lower() in adv["name"].lower()]
    return [app_commands.Choice(name=adv_name, value=adv_name) for adv_name in possible_adventures[:25]]







class ConfirmDeleteRoomButton(discord.ui.Button):
    def __init__(self, label: str, room_id: str, style: discord.ButtonStyle = discord.ButtonStyle.danger, row: int = 0):
        super().__init__(label=label, style=style, row=row)
        self.room_id = room_id
    async def callback(self, interaction: discord.Interaction):
        # Assuming 'database' is your database handler and 'testrooms' is the collection for rooms
        room = database.testrooms.find_one({"roomid": self.room_id})
        if room and interaction.user.id == int(room.get("author")):
            delete_result = database.testrooms.delete_one({"roomid": self.room_id})
            if delete_result.deleted_count > 0:
                await interaction.response.send_message(f"Room with ID '{self.room_id}' has been deleted.", ephemeral=True)
            else:
                await interaction.response.send_message("No room found with that ID to delete.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to delete this room or it does not exist.", ephemeral=True)
# Update the deleteroom command to include a confirmation button


@bot.tree.command(name="deleteroom", description="Delete a room by its ID")
async def deleteroom(interaction: discord.Interaction, room_id: str):
    # Retrieve room information from the database based on room_id
    room = database.testrooms.find_one({"roomid": room_id})
    if room:
        # Check if the user has permission to delete the room
        if interaction.user.id == int(room.get("author")):
            view = discord.ui.View()
            # Add the confirm delete room button to the view
            view.add_item(ConfirmDeleteRoomButton(label=f"Confirm Deletion of {room_id}", room_id=room_id))
            await interaction.response.send_message(f"Are you sure you want to delete room '{room_id}'?", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to delete this room.", ephemeral=True)
    else:
        await interaction.response.send_message("Room not found.", ephemeral=True)

@deleteroom.autocomplete('room_id')
async def autocomplete_room_id_deletion(interaction: discord.Interaction, current: str):
            # Query the database for room IDs created by the user, using regex for filtering based on the current input
            room_ids_query = database.testrooms.find(
                {"author": interaction.user.id, "roomid": {"$regex": re.escape(current), "$options": "i"}},
                {"roomid": 1, "_id": 0}
            )
            # Fetch up to 25 room IDs for the autocomplete suggestions
            room_ids = [room["roomid"] for room in room_ids_query.limit(25)]
            # Create choices for each suggestion
            return [app_commands.Choice(name=room_id, value=room_id) for room_id in room_ids]



class ConfirmDeleteButton(discord.ui.Button):
  def __init__(self, label: str, item_id: str, style: discord.ButtonStyle = discord.ButtonStyle.danger, row: int = 0):
      super().__init__(label=label, style=style, row=row)
      self.item_id = item_id
  async def callback(self, interaction: discord.Interaction):
      item = database.testitems.find_one({"itemid": self.item_id})
      if item and interaction.user.id == item.get("author"):
          delete_result = database.testitems.delete_one({"itemid": self.item_id})
          if delete_result.deleted_count > 0:
              await interaction.response.send_message(f"Item with ID '{self.item_id}' has been deleted.", ephemeral=True)
          else:
              await interaction.response.send_message("No item found with that ID to delete.", ephemeral=True)
      else:
          await interaction.response.send_message("You do not have permission to delete this item or it does not exist.", ephemeral=True)


class ConfirmDeleteItemButton(discord.ui.Button):
  def __init__(self, label: str, item_id: str, style: discord.ButtonStyle = discord.ButtonStyle.danger, row: int = 0):
      super().__init__(label=label, style=style, row=row)
      self.item_id = item_id
  async def callback(self, interaction: discord.Interaction):
      item = database.testitems.find_one({"itemid": self.item_id})
      if item and interaction.user.id == item.get("author"):
          delete_result = database.testitems.delete_one({"itemid": self.item_id})
          if delete_result.deleted_count > 0:
              await interaction.response.send_message(f"Item with ID '{self.item_id}' has been deleted.", ephemeral=True)
          else:
              await interaction.response.send_message("No item found with that ID to delete.", ephemeral=True)
      else:
          await interaction.response.send_message("You do not have permission to delete this item or it does not exist.", ephemeral=True)
@bot.tree.command(name="deleteitem", description="Delete an item by its ID")
async def deleteitem(interaction: discord.Interaction, item_id: str):
  item = database.testitems.find_one({"itemid": item_id})
  if item and interaction.user.id == item.get("author"):
      view = discord.ui.View()
      view.add_item(ConfirmDeleteItemButton(label=f"Confirm Deletion of {item_id}", item_id=item_id))
      await interaction.response.send_message(f"Are you sure you want to delete item '{item_id}'?", view=view, ephemeral=True)
  else:
      await interaction.response.send_message("You do not have permission to delete this item or it does not exist.", ephemeral=True)
@deleteitem.autocomplete('item_id')
async def autocomplete_item_id_deletion(interaction: discord.Interaction, current: str):
  # Query the database for item IDs created by the user, using regex for filtering based on the current input
  item_ids_query = database.testitems.find(
      {"author": interaction.user.id, "itemid": {"$regex": re.escape(current), "$options": "i"}},
      {"itemid": 1, "_id": 0}
  )
  # Fetch up to 25 item IDs for the autocomplete suggestions
  item_ids = [item["itemid"] for item in item_ids_query.limit(25)]
  # Create choices for each suggestion
  return [app_commands.Choice(name=item_id, value=item_id) for item_id in item_ids]

@bot.tree.command(name="editadventure", description="Edit adventure properties")
@app_commands.choices(field=[
  app_commands.Choice(name="Name", value="nameid"),
  app_commands.Choice(name="Starting Room", value="start"),
  app_commands.Choice(name="Description", value="description")
])
async def editadventure(interaction: discord.Interaction, nameid: str, field: app_commands.Choice[str], value: str):
  # Retrieve adventure and verify author
  adventure = database.testadventures.find_one({"nameid": nameid})
  if adventure and interaction.user.id == adventure.get("author"):
      button_label = f"Confirm editing {field.name}"  # Use field.name for a human-readable label
      view = discord.ui.View()
      view.add_item(ConfirmEditAdventureButton(
          label=button_label, nameid=nameid, field=field, value=value  # Pass the entire 'field' choice
      ))
      await interaction.response.send_message(f"Are you sure you want to change '{field.name}' to '{value}'?", view=view, ephemeral=True)
  else:
      await interaction.response.send_message("Adventure not found or you do not have permission to edit this adventure.", ephemeral=True)
class ConfirmEditAdventureButton(discord.ui.Button):
  def __init__(self, label: str, nameid: str, field: app_commands.Choice[str], value: str, style: discord.ButtonStyle = discord.ButtonStyle.success, row: int = 0):
      super().__init__(label=label, style=style, row=row)
      self.nameid = nameid
      self.field = field.value  # Use the 'value' as it contains the field key for DB operations
      self.value = value
      self.field_name = field.name  # Store the field name for display purposes
  async def callback(self, interaction: discord.Interaction):
      if self.disabled:
          return
      # Update the adventure in the database using the field value
      update_result = database.testadventures.update_one(
          {"nameid": self.nameid},
          {"$set": {self.field: self.value}}
      )
      if update_result.modified_count > 0:
          await interaction.response.edit_message(content=f"Adventure '{self.nameid}' successfully updated: {self.field_name} set to {self.value}.", view=None)
      else:
          await interaction.response.edit_message(content=f"Update failed or no changes made to the adventure '{self.nameid}'.", view=None)
      self.disabled = True  # Disable the button after the action
      await interaction.message.edit(view=self.view)  # Refresh the view to show the disabled button state
# Autocompletion for nameid parameter in editadventure
@editadventure.autocomplete('nameid')
async def autocomplete_adventure_nameid(interaction: discord.Interaction, current: str):
  # Query the database for adventure nameids, filtering based on the current input
  adventures_query = database.testadventures.find(
      {"nameid": {"$regex": "^" + re.escape(current), "$options": "i"}},
      {"nameid": 1, "_id": 0},
  ).limit(25)
  adventure_nameids = [adv["nameid"] for adv in adventures_query]
  return [app_commands.Choice(name=nameid, value=nameid) for nameid in adventure_nameids]


class ConfirmDeleteAdventureButton(discord.ui.Button):
def __init__(self, label: str, style: discord.ButtonStyle = discord.ButtonStyle.danger, row: int = 0):
    super().__init__(label=label, style=style, row=row)

async def callback(self, interaction: discord.Interaction):
    # Assuming 'database' is your database handler and 'testadventures' is the collection for adventures
    adventure = database.testadventures.find_one({"nameid": self.view.nameid})
    if adventure and interaction.user.id == adventure.get("author"):
        delete_result = database.testadventures.delete_one({"nameid": self.view.nameid})
        if delete_result.deleted_count > 0:
            await interaction.response.send_message(f"Adventure '{self.view.nameid}' has been deleted.", ephemeral=True)
        else:
            await interaction.response.send_message("No adventure found with that ID to delete.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to delete this adventure or it does not exist.", ephemeral=True)
class ConfirmDeleteAdventureView(discord.ui.View):
def __init__(self, nameid: str):
    super().__init__()
    self.nameid = nameid
    self.add_item(ConfirmDeleteAdventureButton(label=f"Confirm Deletion"))


@bot.tree.command(name="deleteadventure", description="Delete an adventure by its name ID")
async def deleteadventure(interaction: discord.Interaction, nameid: str):
adventure = database.testadventures.find_one({"nameid": nameid})
if adventure and interaction.user.id == adventure.get("author"):
    view = ConfirmDeleteAdventureView(nameid=nameid)
    await interaction.response.send_message(f"Are you sure you want to delete adventure '{nameid}'?", view=view, ephemeral=True)
else:
    await interaction.response.send_message("You do not have permission to delete this adventure or it does not exist.", ephemeral=True)

@bot.tree.command(name="leave", description="Leave the current adventure")
async def leave(interaction: discord.Interaction):
  author_id = interaction.user.id
  player_info = database.get_player(author_id)
  if player_info:
      thread_id = player_info.get("game_thread_id")
      if thread_id:
          # Create a view and add the ConfirmLeaveButton
          view = discord.ui.View()
          view.add_item(ConfirmLeaveButton(label="Confirm Leave", style=discord.ButtonStyle.danger, thread_id=thread_id, bot_name=player_info.get('bot_name')))
          await interaction.response.send_message("Are you sure you want to leave the adventure?", view=view, ephemeral=True)
      else:
          await interaction.response.send_message("You don't seem to be in any active game thread.", ephemeral=True)
  else:
      await interaction.response.send_message("You are not part of any adventure to leave.", ephemeral=True)



class ConfirmLeaveButton(discord.ui.Button):
  def __init__(self, label, style, thread_id, bot_name, row=0):
      super().__init__(label=label, style=style, row=row)
      self.thread_id = thread_id
      self.bot_name = bot_name
  async def callback(self, interaction: discord.Interaction):
      # Retrieve the thread object using the thread ID
      thread = interaction.guild.get_thread(self.thread_id)
      if thread:
          # Assuming `leave_game` is a coroutine that handles leaving logic:
          await leave_game(interaction, thread, self.bot_name)
          # Delete the thread after the player has left the game
          await interaction.response.send_message("You have left the adventure, and the game thread has been deleted.", ephemeral=True)
          await thread.delete()
      else:
          await interaction.response.send_message("Failed to find the game thread to leave.", ephemeral=True)

      # Disable the button after it has been used
      self.disabled = True
      # Update the button's appearance on the message
      await interaction.message.edit(view=self.view)





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
          array_updates = {}
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
          result = database.examples.find_one({"roomid": roomid })
          if result:
              embed = discord.Embed(title=result["roomid"], description="this is the example.", color=0x00ff00)
              fields = ["displayname", "description", "kill","URL", "items"]
              arrayfields = ["exits", "exit_destination"] 
              arrayfieldss = ["secrets", "unlockers"]
              for field in fields: 
                embed.add_field(name= field, value=result[field], inline=False)
              for field in arrayfields: 
                embed.add_field(name= field, value="\n".join(result[field]), inline=True)
              embed.add_field(name = "", value = "", inline=False )
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
    example_room_ids_query = database.examples.find(
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
    player_info = database.get_player(truename)
    if player_info and player_info["edit_thread_id"] != "":
        embed = formatter.blank_embed(name, "Error", "You already have an existing thread for editing adventures. Please use that for editing your adventure.", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    # Check for the player existing in the database
    elif not player_info:
        embed = formatter.blank_embed(name, "Error", "You are not a player. Please use /join Example Adventure to begin", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    # Checks for the player having joined the example adventure
    elif player_info["current_adventure"] != "example adventure":
        embed = formatter.blank_embed(name, "Error", "You are not in the Example Adventure. Please use /join Example Adventure to begin", "red")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
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

#Leaves current game
@bot.tree.command(name= "leave", description= "Use this command to leave the game! (You can only leave if you are the host of the game)")
async def leave(interaction: discord.Interaction):
    truename = interaction.user.id
    name = interaction.user.display_name 
    player = database.get_player(truename)
    if player:
      channel = bot.get_channel(player["channel"])
      tuple = await database.confirm_embed("Leaving the game will delete all of your data and delete this thread. Click *Yes* to continue or *No* to cancel:", "leave" , channel)
      embed = tuple[0]
      view = tuple[1]
    else:
      embed = formatter.embed_message(name, "Error", "notplayer" , "red")
      view = discord.ui.View()
    await interaction.response.send_message(embed=embed, view=view)

#replies with the description of the current room to the player
@bot.tree.command(name= "info", description= "Learn about the room you are in")
async def info(interaction: discord.Interaction):
  truename = interaction.user.id
  player = database.get_player(truename)
  if player:
    if player["alive"]:
        room_name = player["room"]
        all_items = player["inventory"]
        new_items = []
        room = database.get_room(room_name)
    else:
      await interaction.response.send_message("You are either dead or not in a adventure!")
      return
    if room:
      tuple = database.embed_room(all_items, new_items, room["displayname"], room)
    else:
      return
    embed = tuple[0]
    view = tuple[1]
    await interaction.response.send_message(embed=embed, view=view)



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
        print(f"Author ID: {author_id}")
        author = guild.get_member(author_id)
        if author:
            authors.append(author.display_name)
        else:
            authors.append("Unknown Author")
    embed = discord.Embed(title="Adventures", description="These are the adventures you can join. Use !newgame to start the test adventure. More adventures will be available later!", color=0x00ff00)
    for i in range(len(adventure_names)):
      embed.add_field(name=adventure_names[i].title(), value=descriptions[i] + "\nCreated by: " + authors[i], inline=False)
    await interaction.response.send_message(embed=embed)
    return

#prints a connection message to the console for debugging
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
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
