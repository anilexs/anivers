import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID utilisateur

class OffSondage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="offsondage", description="Remettre un sondage posté en attente (posted=0)")
    @app_commands.describe(id="L'identifiant du sondage à remettre en attente")
    async def offsondage(self, interaction: discord.Interaction, id: int):
        author = interaction.user
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID) if guild else None
        is_admin = admin_role in author.roles if admin_role else False
        is_owner = author.id == OWNER_ID
        if not (is_admin or is_owner):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute("SELECT posted FROM sondage WHERE id = ?", (id,))
            row = cursor.fetchone()
            if not row:
                await interaction.response.send_message(f"❌ Aucun sondage trouvé avec l'ID {id}.", ephemeral=True)
                conn.close()
                return
            if row[0] == 0:
                await interaction.response.send_message(f"ℹ️ Le sondage {id} est déjà en attente.", ephemeral=True)
                conn.close()
                return
            cursor.execute("UPDATE sondage SET posted = 0 WHERE id = ?", (id,))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"✅ Le sondage {id} a été remis en attente (posted = 0).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(OffSondage(bot))
