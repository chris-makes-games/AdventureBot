import discord
from button import B

class View(discord.ui.View):
  @B(label="Button 1", destination="test")
  async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message(button.destination)