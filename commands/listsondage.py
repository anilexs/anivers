ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID utilisateur
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class SondageView(discord.ui.View):
    def __init__(self, sondages, page, total_pages, author_id):
        super().__init__(timeout=60)
        self.sondages = sondages
        self.page = page
        self.total_pages = total_pages
        self.author_id = author_id
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.page > 0:
            self.add_item(PrevButton())
        if self.page < self.total_pages - 1:
            self.add_item(NextButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

class PrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label='⬅️ Page précédente')

    async def callback(self, interaction: discord.Interaction):
        view: SondageView = self.view
        await send_sondage_page(interaction, view.page - 1, view.author_id)

class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label='Page suivante ➡️')

    async def callback(self, interaction: discord.Interaction):
        view: SondageView = self.view
        await send_sondage_page(interaction, view.page + 1, view.author_id)

async def send_sondage_page(interaction, page, author_id, first=False):
    per_page = 5
    offset = page * per_page
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, options, emojis FROM sondage WHERE posted = 0 ORDER BY id ASC LIMIT ? OFFSET ?", (per_page, offset))
    rows = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM sondage WHERE posted = 0")
    total = cursor.fetchone()[0]
    conn.close()
    total_pages = (total + per_page - 1) // per_page

    embed = discord.Embed(
        title=f"📋 Sondages non postés (page {page+1}/{total_pages})",
        color=discord.Color.blurple()
    )
    if not rows:
        embed.description = "Aucun sondage à afficher."
    else:
        for row in rows:
            id, question, options_str, emojis_str = row
            options = options_str.split('%')
            emojis = [e.replace('\\', '') for e in emojis_str.split('%')]
            opt_emo = '\n'.join([f"{emojis[i] if i < len(emojis) else ''} {options[i]}" for i in range(len(options))])
            embed.add_field(name=f"ID: {id} | {question}", value=opt_emo, inline=False)

    view = SondageView(rows, page, total_pages, author_id)
    if first:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
        await interaction.response.edit_message(embed=embed, view=view)

class ListSondage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="listsondage", description="Affiche les sondages non postés avec pagination")
    async def listsondage(self, interaction: discord.Interaction):
        author = interaction.user
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID) if guild else None
        is_admin = admin_role in author.roles if admin_role else False
        is_owner = author.id == OWNER_ID
        if not (is_admin or is_owner):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return
        await send_sondage_page(interaction, 0, interaction.user.id, first=True)

async def setup(bot):
    await bot.add_cog(ListSondage(bot))
