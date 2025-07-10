import discord
from discord.ext import commands
from discord import app_commands
import json

class ResteSondages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="restesondages", description="Affiche le nombre de sondages non postés")
    async def restesondages(self, interaction: discord.Interaction):
        try:
            with open("sondages.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            restants = [s for s in data if not s.get("posted", False)]
            total = len(restants)

            # Choix de la couleur : vert si ≥ 5, rouge sinon
            color = discord.Color.green() if total >= 3 else discord.Color.red()

            embed = discord.Embed(
                title="📊 Sondages restants",
                description=f"Il reste **{total}** sondage(s) à publier.",
                color=color
            )

            await interaction.response.send_message(embed=embed)

        except FileNotFoundError:
            await interaction.response.send_message("❌ Le fichier `sondages.json` est introuvable.")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}")

async def setup(bot):
    await bot.add_cog(ResteSondages(bot))
