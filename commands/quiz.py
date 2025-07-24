import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random

class QuizButton(discord.ui.Button):
    def __init__(self, label: str, index: int):
        super().__init__(style=discord.ButtonStyle.primary, label=label, custom_id=str(index))
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: QuizView = self.view
        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ Ce n'est pas à toi de répondre !", ephemeral=True)
            return

        if view.answered:
            await interaction.response.send_message("Tu as déjà répondu.", ephemeral=True)
            return

        view.answered = True

        embed = interaction.message.embeds[0]

        if self.index == view.correct_index:
            result_message = "\n\n✅ **Bravo, c'est la bonne réponse !**"
        else:
            result_message = "\n\n❌ **Mauvaise réponse... Veuillez réessayer la prochaine fois !**"

        embed.description += result_message

        # Désactive tous les boutons
        for child in view.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=view)


class QuizView(discord.ui.View):
    def __init__(self, options: list[str], correct_index: int, user_id: int, timeout=120):
        super().__init__(timeout=timeout)
        self.correct_index = correct_index
        self.user_id = user_id
        self.answered = False

        for idx, option in enumerate(options):
            self.add_item(QuizButton(label=option, index=idx))


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_theme_choices(self) -> list[app_commands.Choice[str]]:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM theme_quiz ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [app_commands.Choice(name=row[0], value=row[0]) for row in rows]

    @app_commands.command(
        name="quiz",
        description="Joue à un quiz dans un thème choisi"
    )
    @app_commands.describe(theme="Choisis le thème du quiz")
    @app_commands.autocomplete(theme="theme_autocomplete")
    async def quiz(self, interaction: discord.Interaction, theme: str):
        # Récupérer un quiz aléatoire dans le thème
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT q.id, q.question, q.options, q.correct_index 
            FROM question_quiz q
            JOIN link_quiz_theme l ON q.id = l.quiz_id
            JOIN theme_quiz t ON l.theme_id = t.id
            WHERE t.name = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (theme,))
        quiz_data = cursor.fetchone()
        conn.close()

        if not quiz_data:
            await interaction.response.send_message(f"❌ Aucun quiz trouvé pour le thème '{theme}'.", ephemeral=True)
            return

        quiz_id, question, options_str, correct_index = quiz_data
        options = [opt.strip() for opt in options_str.split(";") if opt.strip()]

        embed = discord.Embed(
            title=f"🎲 Quiz : {theme}",
            description=f"**{question}**\n\n" + "\n".join(f"{idx+1}. {opt}" for idx, opt in enumerate(options)),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Clique sur le bouton correspondant à ta réponse")

        view = QuizView(options=options, correct_index=correct_index, user_id=interaction.user.id)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @quiz.autocomplete("theme")
    async def theme_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = await self.get_theme_choices()
        return [choice for choice in choices if current.lower() in choice.name.lower()][:25]


async def setup(bot):
    await bot.add_cog(Quiz(bot))
