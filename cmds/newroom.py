from discord.ext import commands
import database
import formatter

#Makes a new room in the database
@commands.hybrid_command(name= "newroom", description= "Create a blank new room")
async def newroom(ctx):
  truename = ctx.author.id
  name = ctx.author.display_name
  try:
    database.create_blank_room(truename)
    embed = formatter.blank_embed(name, "Success", "Room was created, use the get room command /getroom  to view the room you just made.", "green")
  except Exception as e:
    embed = formatter.blank_embed(name, "Error", str(e), "red")
    await ctx.reply(embed=embed, ephemral=True)