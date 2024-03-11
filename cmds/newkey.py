from discord.ext import commands
import database
import formatter

#Makes a new blank key in the database
@commands.hybrid_command(name= "newkey", description= "Create a new key")
async def newkey(ctx):
  author_id = ctx.author.id
  name = ctx.author.display_name
  try:
    database.create_new_key(author_id)
    embed = formatter.blank_embed(name, "Success", "Key was created", "green")
  except Exception as e:
    embed = formatter.blank_embed(name, "Error", str(e), "red")
    await ctx.reply(embed=embed, ephemral=True)

async def setup(bot):
  bot.add_command(newkey)