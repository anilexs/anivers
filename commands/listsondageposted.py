import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
OWNER_ID = 457553583919857666  # Ton ID utilisateur

SONDAGES_PAR_PAGE = 5

class SondagePostedView(discord.ui.View):
    def __init__(self, sondages, page, total_pages, author_id):
        super().__init__(timeout=60)
        self.sondages = sondages
        self.page = page
        self.total_pages = total_pages
        self.author_id = author_id
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.page > 1:
            self.add_item(self.PrevButton(self))
        if self.page < self.total_pages:
            self.add_item(self.NextButton(self))

    class PrevButton(discord.ui.Button):
        def __init__(self, view):
            super().__init__(style=discord.ButtonStyle.primary, label='⬅️ Précédent')
            self.view_ref = view
        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != self.view_ref.author_id:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser cette pagination.", ephemeral=True)
                return
            await self.view_ref.show_page(interaction, self.view_ref.page - 1)

    class NextButton(discord.ui.Button):
        def __init__(self, view):
            super().__init__(style=discord.ButtonStyle.primary, label='Suivant ➡️')
            self.view_ref = view
        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != self.view_ref.author_id:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser cette pagination.", ephemeral=True)
                return
            await self.view_ref.show_page(interaction, self.view_ref.page + 1)

    async def show_page(self, interaction, new_page):
        offset = (new_page - 1) * SONDAGES_PAR_PAGE
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, question FROM sondage WHERE posted = 1 ORDER BY id ASC LIMIT ? OFFSET ?", (SONDAGES_PAR_PAGE, offset))
        sondages = cursor.fetchall()
        conn.close()
        self.page = new_page
        self.sondages = sondages
        embed = get_posted_embed(sondages, new_page, self.total_pages)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)


def get_posted_embed(sondages, page, total_pages):
    embed = discord.Embed(title=f"Sondages postés (page {page}/{total_pages})", color=0x00bfff)
    if not sondages:
        embed.description = "Aucun sondage posté."
    else:
        for s in sondages:
            embed.add_field(name=f"ID: {s[0]}", value=s[1], inline=False)
    return embed

class ListSondagePosted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="listsondageposted", description="Liste les sondages déjà postés (5 par page)")
    async def listsondageposted(self, interaction: discord.Interaction, page: int = 1):
        author = interaction.user
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID) if guild else None
        is_admin = admin_role in author.roles if admin_role else False
        is_owner = author.id == OWNER_ID
        if not (is_admin or is_owner):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sondage WHERE posted = 1")
        total = cursor.fetchone()[0]
        total_pages = max(1, (total + SONDAGES_PAR_PAGE - 1) // SONDAGES_PAR_PAGE)
        if page < 1 or page > total_pages:
            page = 1
        offset = (page - 1) * SONDAGES_PAR_PAGE
        cursor.execute("SELECT id, question FROM sondage WHERE posted = 1 ORDER BY id ASC LIMIT ? OFFSET ?", (SONDAGES_PAR_PAGE, offset))
        sondages = cursor.fetchall()
        conn.close()
        embed = get_posted_embed(sondages, page, total_pages)
        view = SondagePostedView(sondages, page, total_pages, author.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ListSondagePosted(bot))
