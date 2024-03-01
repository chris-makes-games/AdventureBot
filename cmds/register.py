from discord.ext import commands

import database
import perms_ctx as permissions


#allows the bot to post messages in the channel
@commands.hybrid_command(name="register", description="Register a bot to a channel")
async def register(ctx):
  #user must be admin, owner, or an architect to use command
  if not permissions.check_all(ctx):
    await ctx.reply("You do not have permission to use this command.")
    return
  channel_id = ctx.channel.id
  guild_id = ctx.guild.id
  if database.register_channel(channel_id, guild_id):
    await ctx.reply("Bot has been registered to this channel.", ephemeral=True)
    print(f"Bot has been registered to channel: {channel_id}")
  else:
    await ctx.reply("Failed to register the bot: guild already has this channel registered.", ephemeral=True)
    print("Error in register command: guild already has this channel in the database")

async def setup(bot):
  bot.add_command(register)