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
      #print(f"\nRoom {room_id} not found in database!")
      continue
    #print(f"\nfound room: {room_id}:")
    #database.pp(found_room["displayname"])
    #print(f"exits: {found_room['exits']}")
    if len(found_room["displayname"]) > 10:
      room_label = f"{found_room['displayname'][0:10]}...\n{found_room['id']}"
    else:
      room_label = f"{found_room['displayname']}\n{found_room['id']}"
    labels[found_room['id']] = room_label
    G.add_node(found_room['id'])
    if found_room["end"]:
      color = "purple"
    elif not found_room["exits"]:
      #print(f"No exits for room: {found_room['id']}")
      #print(found_room["exits"])
      color = "red"
    elif found_room["once"]:
      color = "yellow"
    elif adventure["start"] == found_room["id"]:
      color = "green"
    else:
      color = "skyblue"
    color_map.append(color if color else "gray")
    #print(f"Added node: {found_room['id']}")
    #print(f"adding color: {color}")
    #print("colors so far:")
    #database.pp(color_map)
    for connected_room_id in found_room["exits"]:
      if connected_room_id == found_room["id"]:
        #print("circular room! skipping...")
        continue
      G.add_edge(found_room['id'], connected_room_id)
      #print(f"Added edge: {found_room['id']} -> {connected_room_id}")
    
  #print("Number of nodes in graph:", len(G.nodes))
  #print("Length of color map:", len(color_map))

  for edge in G.edges:
    print(f"edge {edge[0]} -> {edge[1]}")
  database.pp(G.nodes)
  pos = nx.spring_layout(G, k=0.9, iterations=50)
  nx.draw_networkx(G, pos, labels=labels, node_size=2500, font_size=12, font_weight="bold", margins=0.1, arrowsize=20, edge_color="gray", node_color=color_map, width=1.5)
  plt.box(False)

  # Save the plot to a buffer
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  file = discord.File(buffer, filename="image.png")
  
  # Clear the plot to avoid overlapping plots
  plt.clf()
  plt.close()
  color_map.clear()
  labels.clear()
  return file
