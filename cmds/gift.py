from discord.ext import commands

import discord

import database

#secret santa command
@commands.hybrid_command(name= "gift", description= "Use to sign up for the SizeFiction gift exchange")
async def gift(ctx):
  truename = ctx.author.id
  # comment out for getting logs of all participants
  # if truename == 267389442409496578:
  #   print("sarnt found")
  #   all_gifts = database.gifts.find()
  #   for gift in all_gifts:
  #     embed = discord.Embed(title=gift['displayname'])
  #     for key, value in gift.items():
  #       if key == "disc" or key == "_id" or key == "displayname":
  #         continue
  #       embed.add_field(name=key, value=value)
  #     await ctx.reply(embed=embed, ephemeral=True)
  print("sending gift modal to " + ctx.author.display_name)
  tuple = await database.gifts_embed(ctx.interaction.id, truename)
  embed = tuple[0]
  view = tuple[1]
  await ctx.reply(embed=embed, view=view, ephemeral=True)

async def setup(bot):
  bot.add_command(gift)