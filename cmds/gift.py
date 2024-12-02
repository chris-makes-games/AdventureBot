from discord.ext import commands

import discord

import database

#secret santa command
@commands.hybrid_command(name= "gift", description= "Use to sign up for the winter gift exchange")
async def gift(ctx):
  truename = ctx.author.id
  if truename == 267389442409496578:
    type = 0
    all_gifts = database.gifts.find()
    for gift in all_gifts:
      embed = discord.Embed(title=gift['displayname'])
      for key, value in gift.items():
        if key == "disc" or key == "_id" or key == "displayname":
          continue
        embed.add_field(name=key, value=value)
      await ctx.reply(embed=embed, ephemeral=True)
    return
  tuple = await database.gifts_embed(truename)
  embed = tuple[0]
  view = tuple[1]
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(gift)