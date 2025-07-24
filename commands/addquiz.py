import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID

# ----------- UI POUR LA SÉLECTION DE THÈMES -----------

class ThemeSelect(discord.ui.Select):
    def __init__(self, themes: list[str]):
        options = [
            discord.SelectOption(label=theme, value=theme)
            for theme in themes
        ]
        super().__init__(
            placeholder="Choisis les thèmes...",
            min_values=1,
            max_values=len(options),  # Permet sélection illimitée
            options=options
        )
        self.selected_themes = []

    async def callback(self, interaction: discord.Interaction):
        self.selected_themes = self.values
        await interaction.response.defer()  # Délais le traitement (sera géré par le bouton)

class ThemeSelectView(discord.ui.View):
    def __init__(self, themes: list[str], timeout=60):
        super().__init__(timeout=timeout)
        self.theme_select = ThemeSelect(themes)
        self.add_item(self.theme_select)
        self.value = None  # Stockera la sélection finale

    @discord.ui.button(label="Valider", style=discord.ButtonStyle.green)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.theme_select.selected_themes:
            await interaction.response.send_message("❌ Tu dois sélectionner au moins un thème.", ephemeral=True)
            return
        self.value = self.theme_select.selected_themes
        self.stop()
        await interaction.response.edit_message(
            content=f"✅ Thèmes sélectionnés : {', '.join(self.value)}",
            view=None
        )

# ----------- COMMANDE ADDQUIZ -----------

class AddQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, interaction: discord.Interaction):
        if interaction.user.id == OWNER_ID:
            return True

        member = interaction.guild.get_member(interaction.user.id)
        return any(role.id == ADMIN_ROLE_ID for role in member.roles) if member else False

    async def get_theme_choices(self) -> list[str]:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM theme_quiz ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    @app_commands.command(
        name="addquiz",
        description="Ajoute une question quiz avec options et thèmes (sélection multiple)"
    )
    @app_commands.describe(
        question="Texte de la question",
        options="Options séparées par des ';' (ex: rouge;vert;bleu)",
        correct_index="Index (commençant à 1) de la bonne réponse"
    )
    async def addquiz(
        self,
        interaction: discord.Interaction,
        question: str,
        options: str,
        correct_index: int,
    ):
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ Tu n'as pas la permission d'utiliser cette commande.",
                ephemeral=True
            )
            return

        opts = [opt.strip() for opt in options.split(";") if opt.strip()]
        if len(opts) < 2:
            await interaction.response.send_message(
                "⚠️ Il faut au moins 2 options.",
                ephemeral=True
            )
            return

        if not (1 <= correct_index <= len(opts)):
            await interaction.response.send_message(
                f"⚠️ L'index correct doit être entre 1 et {len(opts)}",
                ephemeral=True
            )
            return

        # Récupération des thèmes
        all_themes = await self.get_theme_choices()
        if not all_themes:
            await interaction.response.send_message(
                "❌ Aucun thème disponible dans la base de données.",
                ephemeral=True
            )
            return

        # Sélecteur de thèmes
        view = ThemeSelectView(all_themes)
        await interaction.response.send_message(
            "Sélectionne les thèmes pour cette question :",
            view=view,
            ephemeral=True
        )

        # Attente de la sélection
        timeout = await view.wait()
        if timeout:
            await interaction.edit_original_response(
                content="⏰ Temps écoulé, commande annulée.",
                view=None
            )
            return

        themes = view.value

        # Insertion du quiz en base de données
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO question_quiz (question, options, correct_index) VALUES (?, ?, ?)",
                (question, ";".join(opts), correct_index)
            )
            quiz_id = cursor.lastrowid

            for theme_name in themes:
                cursor.execute("SELECT id FROM theme_quiz WHERE name = ?", (theme_name,))
                result = cursor.fetchone()
                if result:
                    theme_id = result[0]
                    cursor.execute(
                        "INSERT INTO link_quiz_theme (quiz_id, theme_id) VALUES (?, ?)",
                        (quiz_id, theme_id)
                    )

            conn.commit()

            await interaction.edit_original_response(
                content=f"✅ Quiz ajouté avec ID `{quiz_id}`.",
                view=None
            )
        except Exception as e:
            await interaction.edit_original_response(
                content=f"❌ Erreur : {e}",
                view=None
            )
        finally:
            conn.close()

async def setup(bot):
    await bot.add_cog(AddQuiz(bot))
