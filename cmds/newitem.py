from discord.ext import commands
import database
import formatter

#Makes a new blank item in the database
@commands.hybrid_command(name= "newitem", description= "Create a new item")
async def newitem(ctx):
      author_id = ctx.author.id
      name = ctx.author.display_name
      try:
        database.create_blank_item(author_id)  # pass the user ID to create_blank_item
        embed = formatter.blank_embed(name, "Success", "Item was created", "green")
      except Exception as e:
        embed = formatter.blank_embed(name, "Error", str(e), "red")
      await ctx.reply(embed=embed, ephemral=True)