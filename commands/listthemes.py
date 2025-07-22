import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import math

THEMES_PER_PAGE = 8

class ThemePagination(discord.ui.View):
    def __init__(self, theme_list: list[str]):
        super().__init__(timeout=60)
        self.theme_list = theme_list
        self.current_page = 0
        self.total_pages = math.ceil(len(self.theme_list) / THEMES_PER_PAGE)
        self.update_buttons_visibility()

    def get_page_embed(self):
        start = self.current_page * THEMES_PER_PAGE
        end = start + THEMES_PER_PAGE
        page_items = self.theme_list[start:end]
        description = "\n".join(f"- {theme}" for theme in page_items)

        embed = discord.Embed(
            title="📚 Liste des thèmes",
            description=description,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Page {self.current_page + 1} / {self.total_pages}")
        return embed

    def update_buttons_visibility(self):
        # Désactive ou cache les boutons si nécessaire
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "previous":
                    child.disabled = self.current_page == 0
                elif child.custom_id == "next":
                    child.disabled = self.current_page >= self.total_pages - 1

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary, custom_id="previous")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons_visibility()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons_visibility()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

class ListThemes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="listthemes", description="Affiche la liste des thèmes disponibles (avec pagination)")
    async def listthemes(self, interaction: discord.Interaction):
        # Connexion à la base de données
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM theme_quiz ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("❌ Aucun thème trouvé.")
            return

        themes = [row[0] for row in rows]
        view = ThemePagination(themes)

        # Si une seule page, ne pas afficher les boutons
        if view.total_pages <= 1:
            await interaction.response.send_message(embed=view.get_page_embed())
        else:
            await interaction.response.send_message(embed=view.get_page_embed(), view=view)

async def setup(bot):
    await bot.add_cog(ListThemes(bot))
