from discord.ext import commands

@commands.hybrid_command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.display_name}!")

async def setup(bot):
    bot.add_command(hello)