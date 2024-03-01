from discord.ext import commands


#test command to say hello to the user
@commands.hybrid_command(name='hello', with_app_command=True)
async def hello(ctx):
  await ctx.send(f"Hello, {ctx.author.display_name}!")

async def setup(bot):
  bot.add_command(hello)