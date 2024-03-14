import io

import discord
import matplotlib.pyplot as plt
import networkx as nx

import database


def visualize_adventure(adventure):
  G = nx.DiGraph()
  labels = {}
  color_map = []

  for room_id in adventure["rooms"]:
    found_room = database.get_room(room_id)
    if not found_room:
      print(f"Room {room_id} not found in database!")
      continue
    database.pp(found_room["displayname"])
    database.pp(found_room["exits"])
    if len(found_room["displayname"]) > 10:
      room_label = f"{found_room['displayname'][0:10]}...\n{found_room['id']}"
    else:
      room_label = f"{found_room['displayname']}\n{found_room['id']}"
    labels[found_room['id']] = room_label
    G.add_node(found_room['id'])
    if found_room["end"]:
      color = "red"
    elif not found_room["exits"]:
      print(f"No exits for room: {found_room['id']}")
      print(found_room["exits"])
      color = "orange"
    elif found_room["once"]:
      color = "yellow"
    else:
      color = "skyblue"
    color_map.append(color)
    print("colors so far:")
    database.pp(color_map)
    for connected_room_id in found_room["exits"]:
      G.add_edge(found_room['id'], connected_room_id)
      print(f"Added edge: {found_room['id']} -> {connected_room_id}")
    print(f"Added node: {found_room['id']}\n")
    

      
  for edge in G.edges:
    print(f"edge {edge[0]} -> {edge[1]}")
  pos = nx.spring_layout(G, k=1.5, iterations=100)
  nx.draw_networkx(G, pos, labels=labels, node_size=4500, font_size=12, font_weight="bold", margins=0.1, arrowsize=20, edge_color="gray", width=2.0, node_color=color_map)
  plt.box(False)

  # Save the plot to a buffer
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  file = discord.File(buffer, filename="image.png")
  
  # Clear the plot to avoid overlapping plots
  plt.clf()
  plt.close()
  return file
