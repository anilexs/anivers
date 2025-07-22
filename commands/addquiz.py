import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID

class AddQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, interaction: discord.Interaction):
        return (
            interaction.user.id == OWNER_ID or
            any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)
        )

    async def get_theme_choices(self) -> list[app_commands.Choice[str]]:
        # Charge dynamiquement les thèmes depuis la base
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM theme_quiz ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()

        return [app_commands.Choice(name=row[0], value=row[0]) for row in rows]

    @app_commands.command(name="addquiz", description="Ajoute une question quiz avec options et thèmes (multi-select)")
    @app_commands.describe(
        question="Texte de la question",
        options="Options séparées par des ';' (ex: rouge;vert;bleu)",
        correct_index="Index (commençant à 1) de la bonne réponse",
        themes="Thèmes liés à la question (max 3)"
    )
    async def addquiz(
        self,
        interaction: discord.Interaction,
        question: str,
        options: str,
        correct_index: int,
        themes: list[str] = None
    ):
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        opts = [opt.strip() for opt in options.split(";") if opt.strip()]
        if len(opts) < 2:
            await interaction.response.send_message("⚠️ Il faut au moins 2 options.", ephemeral=True)
            return

        if not (1 <= correct_index <= len(opts)):
            await interaction.response.send_message(f"⚠️ L'index correct doit être entre 1 et {len(opts)}", ephemeral=True)
            return

        if themes and len(themes) > 3:
            await interaction.response.send_message("⚠️ Tu ne peux sélectionner que 3 thèmes au maximum.", ephemeral=True)
            return

        # Enregistrement du quiz
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO question_quiz (question, option, correct_index) VALUES (?, ?, ?)",
                (question, ";".join(opts), correct_index)
            )
            quiz_id = cursor.lastrowid

            # Lier aux thèmes
            if themes:
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
            await interaction.response.send_message(f"✅ Quiz ajouté avec ID `{quiz_id}`.")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)
        finally:
            conn.close()

    @addquiz.autocomplete("themes")
    async def themes_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM theme_quiz WHERE name LIKE ?", (f"%{current}%",))
        rows = cursor.fetchall()
        conn.close()

        return [
            app_commands.Choice(name=row[0], value=row[0])
            for row in rows[:25]  # Limite Discord
        ]

async def setup(bot):
    await bot.add_cog(AddQuiz(bot))
