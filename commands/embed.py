import discord
from discord.ext import commands
from discord import app_commands

DEFAULT_COLOR = 0x9b59b6  # Violet Discord par défaut


# Liste des couleurs prédéfinies
COLOR_CHOICES = [
    ("Violet", 0x9b59b6),
    ("Rouge", 0xe74c3c),
    ("Vert", 0x2ecc71),
    ("Bleu", 0x3498db),
    ("Jaune", 0xf1c40f),
    ("Orange", 0xe67e22),
    ("Rose", 0xe84393),
    ("Cyan", 0x00bcd4),
]

class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Envoie un embed personnalisé (titre, texte, image, couleur, etc.)")
    @app_commands.describe(
        titre="Titre de l'embed (optionnel)",
        text="Texte principal (description)",
        couleur="Choisis une couleur (par défaut : Violet)",
        image_url="URL d'une image à afficher (optionnel)",
        thumbnail_url="URL d'une miniature (optionnel)",
        champ_nom="Nom d'un champ personnalisé (optionnel)",
        champ_valeur="Valeur du champ personnalisé (optionnel)",
        footer="Texte du footer (optionnel)",
        salon_id="ID du salon où poster l'embed (optionnel)"
    )
    @app_commands.choices(
        couleur=[app_commands.Choice(name=nom, value=str(val)) for nom, val in COLOR_CHOICES]
    )
    async def embed(
        self,
        interaction: discord.Interaction,
        text: str,
        titre: str = None,
        couleur: app_commands.Choice[str] = None,
        image_url: str = None,
        thumbnail_url: str = None,
        champ_nom: str = None,
        champ_valeur: str = None,
        footer: str = None,
        salon_id: str = None
    ):
        # Limite aux admins et owner
        ADMIN_ROLE_ID = 123  # Remplace par l'ID de ton rôle admin
        OWNER_ID = 457553583919857666  # Ton ID utilisateur
        author = interaction.user
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID) if guild else None
        is_admin = admin_role in author.roles if admin_role else False
        is_owner = author.id == OWNER_ID
        if not (is_admin or is_owner):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        color = DEFAULT_COLOR
        if couleur:
            try:
                color = int(couleur.value)
            except Exception:
                color = DEFAULT_COLOR
        embed = discord.Embed(description=text, color=color)
        if titre:
            embed.title = titre
        if image_url:
            embed.set_image(url=image_url)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        if champ_nom and champ_valeur:
            embed.add_field(name=champ_nom, value=champ_valeur, inline=False)
        if footer:
            embed.set_footer(text=footer)

        channel = interaction.channel
        if salon_id:
            try:
                salon_id_int = int(salon_id)
                salon = interaction.guild.get_channel(salon_id_int)
                if salon and isinstance(salon, discord.TextChannel):
                    channel = salon
                else:
                    await interaction.response.send_message("❌ Salon introuvable ou non textuel.", ephemeral=True)
                    return
            except Exception:
                await interaction.response.send_message("❌ ID de salon invalide.", ephemeral=True)
                return

        # Si on poste dans un autre salon, on répond OK en privé
        if channel.id != interaction.channel.id:
            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Embed envoyé dans <#{channel.id}>.", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EmbedCog(bot))
