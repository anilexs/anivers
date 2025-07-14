
import discord
from discord.ext import commands
from discord import app_commands
from database import ajouter_sondage

ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
OWNER_ID = 457553583919857666       # Remplace par ton propre ID utilisateur

class AddSondage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addsondage", description="Ajoute un sondage à la base de données")
    @app_commands.describe(
        question="La question du sondage",
        options="Liste des options séparées par ;",
        emojis="Liste des emojis séparés par ; (dans le même ordre que les options)"
    )
    async def addsondage(self, interaction: discord.Interaction, question: str, options: str, emojis: str):
        # Vérification des permissions
        author = interaction.user
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID) if guild else None
        is_admin = admin_role in author.roles if admin_role else False
        is_owner = author.id == OWNER_ID
        if not (is_admin or is_owner):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return


        options_list = [opt.strip() for opt in options.split(';') if opt.strip()]
        emojis_list = [em.strip() for em in emojis.split(';') if em.strip()]

        if len(options_list) < 2 or len(options_list) != len(emojis_list):
            await interaction.response.send_message("❌ Il faut au moins 2 options et autant d'emojis que d'options.", ephemeral=True)
            return
        if len(set(emojis_list)) != len(emojis_list):
            await interaction.response.send_message("❌ Il ne faut pas mettre deux fois le même emoji.", ephemeral=True)
            return

        try:
            ajouter_sondage(question, options_list, emojis_list)
            await interaction.response.send_message(f"✅ Sondage ajouté !\n**Question :** {question}\n**Options :** {' | '.join(options_list)}\n**Emojis :** {' '.join(emojis_list)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de l'ajout : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AddSondage(bot))
