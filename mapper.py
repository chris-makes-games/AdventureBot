import io
import os
import discord
import database
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import ArrowStyle

def visualize_adventure(adventure):
  G = nx.DiGraph()
  labels = {}
  color_map = []

  for room_id in adventure["rooms"]:
    found_room = database.get_room(room_id)
    if not found_room:
      print(f"Room {room_id} not found in database!")
      continue
    room_label = f"{found_room['displayname']}\n{found_room['roomid']}"
    labels[found_room['roomid']] = room_label
    G.add_node(found_room['roomid'], node_color="skyblue")
    exit_destinations = found_room['exit_destination']
    if found_room["kill"]:
      color = "red"
    elif not exit_destinations:
      color = "orange"
    else:
      color = "skyblue"
    color_map.append(color)
    for connected_room_id in exit_destinations:
      G.add_edge(found_room['roomid'], connected_room_id)
      print(f"Added edge: {found_room['roomid']} -> {connected_room_id}")
    else:
      print(f"No exit destinations for room: {found_room['roomid']}")

      
  for edge in G.edges:
    print(f"edge {edge[0]} -> {edge[1]}")
  for label in labels:
    print(f"label {label}:\n{labels[label]}\n")
  pos = nx.spring_layout(G, k=1.5, iterations=100)
  nx.draw_networkx(G, pos, labels=labels, node_size=4500, node_color=color_map, font_size=12, font_weight="bold", margins=0.1, arrowsize=20, edge_color="gray", width=2.0)
  plt.box(False)
  plt.axis("off")

  # Save the plot to a buffer
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  file = discord.File(buffer, filename="image.png")
  
  # Clear the plot to avoid overlapping plots
  plt.clf()
  plt.close()
  return file
