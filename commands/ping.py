import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latency = lambda: round(bot.latency * 1000)  # Ping en ms

    @app_commands.command(name="ping", description="Affiche le ping du bot en millisecondes")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = self.latency()
        await interaction.response.send_message(f"🏓 Pong ! Latence : `{latency_ms}ms`")

async def setup(bot):
    await bot.add_cog(Ping(bot))
