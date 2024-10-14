import os  #used to store secrets
import pathlib  #to get commands from command folder

import discord  #all bot functionality
import requests  # for checking rate limit
from discord.ext import commands  #commands for bot

import database  #mongodb database

#token for use with discord API
test = True #SWAP BETWEEN TEST AND LIVE
my_secret = os.environ['TEST_TOKEN'] if test else os.environ['TOKEN'] 


#intents rescricts scope of discord bot
intents = discord.Intents().all()

#the channel ID needs to be in this list
#bot ignores all other channels
protectedchannels = [
  770017224844116031,
  1180274480807956631,
  1180315816294625291,
  1186398826148417707,
  1186464529366921286,
  908522799772102739,
  1183954110513414164,
  1187417491576729620,
  1192186126623064084,
  1273689927305007137
]

#bot will be the async client for running commands
#remove help to replace with my own
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

#sets the parent directory of the bot
BASE_DIR = pathlib.Path(__file__).parent
#this is the command folder directory
#commands are stored in this folder
CMDS_DIR = BASE_DIR / "cmds"

#prints a connection message to the console for debugging
@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  #this should load all commands from commands folder
  for cmd_file in CMDS_DIR.glob("*.py"):
    try:
      if cmd_file.name != "__init__.py":
        if database.inactive_check(cmd_file.name[0:-3]):
          print(f"Skipped command: /{cmd_file.name[:-3]}...")
        else:
          await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")
    except Exception as e:
      print(f"Failed to load command: /{cmd_file.name[:-3]}")
      print(e)
  #No longer sync commmands on startup!
  #use /sync when needed
  # try: 
  #   synced = await bot.tree.sync()
  #   print(f'Synced {len(synced)} commands.')
  # except Exception as e:
  #   print(e)
  print("Commands loaded! Bot is ready!")

#prevents bot from answering its own messages
#requires messages stay in specific channels
#ignores messages that arent commands
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if not message.content.startswith("!"):
    return
  if message.channel.id in protectedchannels:
    await bot.process_commands(message)

#runs the bot and throws generic errors
try:
  print("running")
  database.ping()
  bot.run(my_secret)
except Exception as e:
  print(e)
