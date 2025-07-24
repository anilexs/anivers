import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Remplace avec l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID utilisateur

class AddThemes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, interaction: discord.Interaction) -> bool:
        """Vérifie si l'utilisateur est le propriétaire ou admin dans la guild."""
        if interaction.user.id == OWNER_ID:
            return True
        if not interaction.guild:
            return False  # Pas en guild, pas de rôles

        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            return False
        return any(role.id == ADMIN_ROLE_ID for role in member.roles)

    @app_commands.command(name="addthemes", description="Ajoute un nouveau thème à la base de données")
    @app_commands.describe(theme="Nom du thème à ajouter")
    async def addthemes(self, interaction: discord.Interaction, theme: str):
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        theme = theme.strip().lower()

        # Connexion à la BDD avec gestion automatique de fermeture
        with sqlite3.connect("bot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM theme_quiz WHERE LOWER(name) = ?", (theme,))
            exists = cursor.fetchone()

            if exists:
                await interaction.response.send_message(f"⚠️ Le thème `{theme}` existe déjà.", ephemeral=True)
                return

            cursor.execute("INSERT INTO theme_quiz (name) VALUES (?)", (theme,))
            conn.commit()

        await interaction.response.send_message(f"✅ Thème ajouté : `{theme}`")

async def setup(bot):
    await bot.add_cog(AddThemes(bot))
