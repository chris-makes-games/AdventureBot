import discord

from database import move_player, get_item, get_player, get_room, get_player_info, pp


class Button(discord.ui.Button):
  def __init__(self, label, destination, disabled=False, row=0):
    super().__init__(label=label, style=discord.ButtonStyle.primary)
    self.destination = destination
    self.disabled = disabled
    self.row = row
  async def callback(self, interaction: discord.Interaction):
    player = get_player(interaction.user.id)
    new_room = get_room(self.destination)
    if player:
      all_items = get_player_info(player["disc"], "inventory")
      taken = get_player_info(player["disc"], "taken")
      pp(player)
      channel = interaction.channel
      await channel.create_thread(name="test", auto_archive_duration=1440)
      await interaction.response.send_message(str(player))


def embed_room(all_items, new_items, title, room, color):
  if color == "red":
    color = discord.Color.red()
  elif color == "green":
    color = discord.Color.green()
  elif color == "blue":
    color = discord.Color.blue()
  elif color == "orange":
    color = discord.Color.orange()
  elif color == "purple":
    color = discord.Color.purple()
  elif color == "yellow":
    color = discord.Color.yellow()
  descr = room["description"]
  embed = discord.Embed(title=title, description=descr, color=color)
  view = discord.ui.View()
  if new_items:
    for item in new_items:
      found_item = get_item(item)
      description = found_item["description"] if found_item else "ERROR - ITEM HAS NO NAME"
      embed.add_field(name="You found an item:", value=description, inline=False)
  if len(room["exits"]) == 0:
    embed.add_field(name="Exits", value="There are no exits from this room. This is the end of the line. Unless this room is broken?", inline=False)
  if len(room["exits"]) == 1:
    embed.add_field(
  name="This area has only one way out.", value="Use !path 1 to take it.", inline=False)
  else:
    embed.add_field(name="Choose a Path:", value="Make your choice by clicking a button below:", inline=False)
  r = 1
  for exit in room["exits"]:
    if room["secrets"][r - 1] == "Open":
      button = Button(label=str(exit), destination=room['exit_destination'][r - 1], row = r)
      view.add_item(button)
    elif room["secrets"][r - 1] == "Secret":
      if room["unlockers"][r - 1] in all_items:
        button = Button(label=str(exit), destination=room['exit_destination'][r - 1], row = r)
        view.add_item(button)
    elif room["unlockers"][r - 1] in all_items:
      button = Button(label=str(exit), destination=room['exit_destination'][r - 1], row = r)
      view.add_item(button)
    else:
      button = Button(label=room["secrets"][r - 1], destination=room['exit_destination'][r - 1], disabled=True, row = r)
      view.add_item(button)
    r += 1
  return (embed, view)

    