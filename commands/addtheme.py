import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Remplace avec l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID utilisateur

class AddThemes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, interaction: discord.Interaction):
        """Vérifie si l'utilisateur est le propriétaire ou admin."""
        return (
            interaction.user.id == OWNER_ID or
            any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)
        )

    @app_commands.command(name="addthemes", description="Ajoute un nouveau thème à la base de données")
    @app_commands.describe(theme="Nom du thème à ajouter")
    async def addthemes(self, interaction: discord.Interaction, theme: str):
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        theme = theme.strip().lower()  # Normalisation

        # Connexion à la BDD
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM theme_quiz WHERE LOWER(name) = ?", (theme,))
        exists = cursor.fetchone()

        if exists:
            await interaction.response.send_message(f"⚠️ Le thème `{theme}` existe déjà.", ephemeral=True)
            conn.close()
            return

        cursor.execute("INSERT INTO theme_quiz (name) VALUES (?)", (theme,))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"✅ Thème ajouté : `{theme}`")

async def setup(bot):
    await bot.add_cog(AddThemes(bot))
