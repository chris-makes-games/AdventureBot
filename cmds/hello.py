from discord.ext import commands


#test command to say hello to the user
@commands.hybrid_command(name='hello', with_app_command=True)
async def hello(ctx):
  await ctx.reply(f"Hello, {ctx.author.mention}!", ephemeral=True)

async def setup(bot):
  bot.add_command(hello)