from discord.ext import commands

import database


#resends a room embed to a player 
@commands.hybrid_command(name="resend", description="Resends an embed in case you're getting failed interactions")
async def resend(ctx):
  player = database.get_player(ctx.author.id)
  if not player:
    await ctx.reply(f"{ctx.author.mention} You are not a player! You have no embed to resend. Use /newplayer to get started.", ephemeral=True)
    return
  room = database.get_room(player["room"])
  if not room:
    await ctx.reply(f"{ctx.author.mention} You are not in a room! Use /join to begin an adventure. If you're supposed to be in a room, contact a Ironically-Tall.", ephemeral=True)
    return
  author = ctx.guild.get_member(room["author"]).display_name
  if not author:
    author = "Unknown"
  thread = ctx.guild.get_thread(player["play_thread"])
  if not thread:
    await ctx.reply(f"{ctx.author.mention} It seems the thread you were playing in was deleted... Creating a new thread...", ephemeral=True)
    thread = await ctx.channel.create_thread(name=f"{ctx.author.display_name} playing {room['adventure']}")
  embed, view = await database.embed_room(player_dict=player, new_keys=[], title=room["displayname"], room_dict=room, author=author, guild=ctx.guild)
  await thread.send(f"Resending embed for {ctx.author.mention}...")
  await thread.send(embed=embed, view=view)

async def setup(bot):
  bot.add_command(resend)