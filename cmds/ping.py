from discord.ext import commands


#simple ping command for testing
@commands.hybrid_command()
async def ping(ctx):
  bot = ctx.bot
  print('Pong!! 🏓\n {0}'.format(round(bot.latency, 2)) + " seconds")
  await ctx.reply('Pong!! 🏓\n {0}'.format(round(bot.latency, 2)) + " seconds", ephemeral=True)

async def setup(bot):
  bot.add_command(ping)