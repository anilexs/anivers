import discord
from discord.ext import commands
from discord import app_commands

import sqlite3

class ResteSondages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="restesondages", description="Affiche le nombre de sondages non postés")
    async def restesondages(self, interaction: discord.Interaction):
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sondage WHERE posted = 0")
            total = cursor.fetchone()[0]
            conn.close()

            color = discord.Color.green() if total >= 3 else discord.Color.red()
            embed = discord.Embed(
                title="📊 Sondages restants",
                description=f"Il reste **{total}** sondage(s) à publier.",
                color=color
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}")

async def setup(bot):
    await bot.add_cog(ResteSondages(bot))
