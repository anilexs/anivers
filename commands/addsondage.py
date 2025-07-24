import discord
from discord.ext import commands
from discord import app_commands
from database import ajouter_sondage

ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Remplace par ton propre ID

class AddSondage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processing_users = set()  # Pour empêcher les doubles insertions

    @app_commands.command(
        name="addsondage",
        description="Ajoute un sondage à la base de données"
    )
    @app_commands.describe(
        question="La question du sondage",
        options="Liste des options séparées par ';'",
        emojis="Liste des emojis séparés par ';' (dans le même ordre que les options)"
    )
    async def addsondage(self, interaction: discord.Interaction, question: str, options: str, emojis: str):
        author = interaction.user

        # Anti double clic / double appel
        if author.id in self.processing_users:
            await interaction.response.send_message(
                "⏳ Tu es déjà en train de créer un sondage. Réessaie dans un instant.",
                ephemeral=True
            )
            return

        self.processing_users.add(author.id)

        try:
            guild = interaction.guild
            is_owner = author.id == OWNER_ID
            is_admin = False

            if guild:
                member = guild.get_member(author.id)
                admin_role = guild.get_role(ADMIN_ROLE_ID)
                if member and admin_role:
                    is_admin = admin_role in member.roles

            if not (is_owner or is_admin):
                await interaction.response.send_message(
                    "❌ Tu n'as pas la permission d'utiliser cette commande.",
                    ephemeral=True
                )
                return

            options_list = [opt.strip() for opt in options.split(';') if opt.strip()]
            emojis_list = [em.strip() for em in emojis.split(';') if em.strip()]

            if len(options_list) < 2:
                await interaction.response.send_message(
                    "❌ Il faut au moins 2 options.",
                    ephemeral=True
                )
                return

            if len(options_list) != len(emojis_list):
                await interaction.response.send_message(
                    "❌ Le nombre d'emojis doit correspondre au nombre d'options.",
                    ephemeral=True
                )
                return

            if len(set(emojis_list)) != len(emojis_list):
                await interaction.response.send_message(
                    "❌ Il ne faut pas mettre deux fois le même emoji.",
                    ephemeral=True
                )
                return

            # Ajout du sondage
            ajouter_sondage(question, options_list, emojis_list)

            await interaction.response.send_message(
                f"✅ Sondage ajouté avec succès !\n"
                f"**Question :** {question}\n"
                f"**Options :** {' | '.join(options_list)}\n"
                f"**Emojis :** {' '.join(emojis_list)}",
                ephemeral=True
            )

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Erreur lors de l'ajout : {e}",
                    ephemeral=True
                )
        finally:
            self.processing_users.discard(author.id)

# Chargement du cog
async def setup(bot):
    await bot.add_cog(AddSondage(bot))
