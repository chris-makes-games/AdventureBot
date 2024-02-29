import io
import os

import discord
import database
import matplotlib.pyplot as plt
import networkx as nx
from discord import SyncWebhook
from matplotlib.patches import ArrowStyle


class Room:
    def __init__(self, id, name, connections=None):
        self.id = id
        self.name = name
        if connections is None:
            connections = []
        self.connections = connections

class Adventure:
    def __init__(self, rooms=None):
        if rooms is None:
            rooms = {}
        self.rooms = rooms
    
    def add_room(self, room):
        self.rooms[room.id] = room

def visualize_adventure(adventure):
    G = nx.DiGraph()
    labels = {}
    for room_id, room in adventure.rooms.items():
      labels[room_id] = f"{room.name}\n{room.id}"
      G.add_node(room_id)
      for connected_room_id in room.connections:
        G.add_edge(room_id, connected_room_id) 

    pos = nx.spring_layout(G, k=1.5, iterations=100)
    nx.draw_networkx(G, pos, labels=labels, node_size=2500, node_color="skyblue", font_size=12, font_weight="bold", margins=0.1, arrowsize=20, edge_color="gray", width=2.0)
    plt.box(False)

    # Save the plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    webhook_url = os.environ['WEBHOOK']
    webhook = SyncWebhook.from_url('https://discord.com/api/webhooks/' + webhook_url)

    embed = discord.Embed(title="Adventure Room Layout")
    embed.set_image(url="attachment://image.png")

    webhook.send(embed=embed, file=discord.File(buffer, "image.png"))

def generate_map(rooms_list):
    all_rooms = database.get_all_rooms()
    adventure = Adventure()
    mapped_rooms = {}
    for room_id in rooms_list:
      room_displayname = all_rooms[room_id].displayname
      connections = all_rooms[room_id].exit_destination
      room = Room(room_id, room_displayname)
  

def example():
  adventure = Adventure()

  room1 = Room("1x4E", "Kitchen1", ["2RtY", "ik9H"])
  room2 = Room("2RtY", "Dining Room", ["1x4E"])
  room3 = Room("ik9H", "Living Room", ["1x4E", "bn24", "z99q"])
  room4 = Room("bn24", "Kitchen2", ["1x4E"])
  room5 = Room("z99q", "Dead End", [])

  adventure.add_room(room1)
  adventure.add_room(room2)
  adventure.add_room(room3)
  adventure.add_room(room4)
  adventure.add_room(room5)

  visualize_adventure(adventure)