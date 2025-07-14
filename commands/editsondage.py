import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID utilisateur

# Modal pour modifier un sondage
class EditSondageModal(discord.ui.Modal, title="Modifier le sondage"):
    def __init__(self, id, question, options, emojis):
        super().__init__()
        self.id = id

        # Champ pour modifier la question
        self.question_input = discord.ui.TextInput(
            label="Question",
            default=question,
            style=discord.TextStyle.paragraph,
            max_length=300
        )
        self.add_item(self.question_input)

        # Affiche les options séparées par ; dans le champ
        options_display = options.replace('%', ';') if options else ''
        self.options_input = discord.ui.TextInput(
            label="Options (séparées par ;)",
            default=options_display,
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        self.add_item(self.options_input)

        # Affiche les emojis séparés par ; dans le champ
        emojis_display = emojis.replace('%', ';') if emojis else ''
        self.emojis_input = discord.ui.TextInput(
            label="Emojis (séparés par ;)",
            default=emojis_display,
            style=discord.TextStyle.short,
            max_length=200
        )
        self.add_item(self.emojis_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Remplace les ; par % pour la sauvegarde (cohérence avec l'ajout)
        options_db = self.options_input.value.replace(';', '%')
        emojis_db = self.emojis_input.value.replace(';', '%')
        # Vérification des doublons d'emojis
        emojis_list = [em.strip() for em in self.emojis_input.value.split(';') if em.strip()]
        if len(set(emojis_list)) != len(emojis_list):
            await interaction.response.send_message("❌ Il ne faut pas mettre deux fois le même emoji.", ephemeral=True)
            return
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sondage SET question = ?, options = ?, emojis = ? WHERE id = ?",
                (self.question_input.value, options_db, emojis_db, self.id)
            )
            conn.commit()
            conn.close()
            await interaction.response.send_message(
                f"✅ Sondage #{self.id} modifié !\n> **Question :** {self.question_input.value}\n> **Options :** {self.options_input.value}\n> **Emojis :** {self.emojis_input.value}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la sauvegarde : {e}", ephemeral=True)

# Commande pour lancer le modal
class EditSondage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="editsondage", description="Modifier un sondage par son ID")
    @app_commands.describe(id="L'identifiant du sondage à modifier")
    async def editsondage(self, interaction: discord.Interaction, id: int):
        author = interaction.user
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID) if guild else None
        is_admin = admin_role in author.roles if admin_role else False
        is_owner = author.id == OWNER_ID

        if not (is_admin or is_owner):
            await interaction.response.send_message(
                "❌ Tu n'as pas la permission d'utiliser cette commande.",
                ephemeral=True
            )
            return

        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute("SELECT question, options, emojis FROM sondage WHERE id = ?", (id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                await interaction.response.send_message(
                    f"❌ Aucun sondage trouvé avec l'ID {id}.",
                    ephemeral=True
                )
                return

            question, options_str, emojis_str = row
            modal = EditSondageModal(id, question, options_str, emojis_str)
            await interaction.response.send_modal(modal)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de la récupération du sondage : {e}",
                ephemeral=True
            )

# Chargement du Cog
async def setup(bot):
    await bot.add_cog(EditSondage(bot))
