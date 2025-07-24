import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random

class QuizView(discord.ui.View):
    def __init__(self, options: list[str], correct_index: int, user_id: int, timeout=60):
        super().__init__(timeout=timeout)
        self.correct_index = correct_index
        self.user_id = user_id
        self.answered = False

        for i, option in enumerate(options):
            self.add_item(QuizButton(label=option, index=i))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce quiz n'est pas pour toi.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass

class QuizButton(discord.ui.Button):
    def __init__(self, label: str, index: int):
        super().__init__(style=discord.ButtonStyle.primary, label=label, custom_id=str(index))
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: QuizView = self.view
        if view.answered:
            await interaction.response.send_message("Tu as déjà répondu.", ephemeral=True)
            return

        view.answered = True

        # Désactive tous les boutons après la réponse
        for child in view.children:
            child.disabled = True

        embed = interaction.message.embeds[0]  # Récupère l'embed actuel

        if self.index == view.correct_index:
            embed.color = discord.Color.green()
            embed.title = embed.title + " ✅"
            embed.description += "\n\n✅ Bravo, c'est la bonne réponse !"
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            embed.color = discord.Color.red()
            embed.title = embed.title + " ❌"
            embed.description += "\n\n❌ Mauvaise réponse... Veuillez réessayer la prochaine fois."
            await interaction.response.edit_message(embed=embed, view=view)

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_themes(self):
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM theme_quiz ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    async def theme_autocomplete(self, interaction: discord.Interaction, current: str):
        themes = self.get_themes()
        return [
            app_commands.Choice(name=theme, value=theme)
            for theme in themes if current.lower() in theme.lower()
        ][:25]

    @app_commands.command(name="quiz", description="Lance un quiz dans un thème")
    @app_commands.describe(theme="Choisis le thème du quiz")
    @app_commands.autocomplete(theme=theme_autocomplete)
    async def quiz(self, interaction: discord.Interaction, theme: str):
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.question, q.options, q.correct_index
            FROM question_quiz q
            JOIN link_quiz_theme l ON q.id = l.quiz_id
            JOIN theme_quiz t ON l.theme_id = t.id
            WHERE t.name = ?
        """, (theme,))
        quizzes = cursor.fetchall()
        conn.close()

        if not quizzes:
            await interaction.response.send_message(f"⚠️ Aucun quiz trouvé pour le thème '{theme}'.", ephemeral=True)
            return

        question, options_str, correct_index = random.choice(quizzes)
        options = [opt.strip() for opt in options_str.split(";") if opt.strip()]

        embed = discord.Embed(
            title=f"🎲 Quiz : {theme}",
            description=question,
            color=discord.Color.blurple()
        )

        view = QuizView(options=options, correct_index=correct_index, user_id=interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        sent_message = await interaction.original_response()
        view.message = sent_message

async def setup(bot):
    await bot.add_cog(Quiz(bot))
