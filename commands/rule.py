import discord
from discord.ext import commands

RULES_CHANNEL_ID = 1393290477272567878
THUMBNAIL_URL = "attachment://anivers.png"

# Emojis personnalisés (à adapter si besoin)
EMOJIS = {
    "zzz": "<:anniZzz:1393304809573978153>",
    "annie": "<:annie:1393304908463214672>",
    "angry": "<:annieAngry:1393305642718204035>",
    "fun": "<:annieFun:1393306141999763589>",
    "heart": "<:annieHeart:1393305527554937043>",
    "heart2eye": "<:annieHeart2eye:1393305203595415605>",
    "reflect": "<:annieReflect:1393305422861045852>",
    "smile": "<:annieSmile:1393295476593266848>",
    "confetti": "<:annieconfetti:1393305109064323253>",
    "cry": "<:anniecry:1393309003706011708>",
    "tear": "<:annietear:1393306010671911002>"
}

RULES = [
    (f"{EMOJIS['smile']} Respect et bienveillance", "Restez courtois avec tous les membres. Les insultes, propos haineux ou discriminatoires sont interdits."),
    (f"{EMOJIS['heart']} Pas de spam", "Évitez le spam, le flood ou la pub non autorisée dans les salons."),
    (f"{EMOJIS['confetti']} Contenu adapté", "Pas de contenu NSFW, choquant ou illégal. Restez dans le thème du serveur."),
    (f"{EMOJIS['fun']} Respect de la vie privée", "Ne partagez pas d'informations personnelles (les vôtres ou celles d'autrui)."),
    (f"{EMOJIS['angry']} Pas de harcèlement", "Le harcèlement, même sous forme de blague, est strictement interdit."),
    (f"{EMOJIS['reflect']} Suivez les consignes du staff", "Le staff se réserve le droit de modérer et de sanctionner si besoin.")
]

class Rule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(RULES_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=f"{EMOJIS['heart2eye']} Règles du serveur",
                description="Bienvenue sur le serveur ! Merci de lire et respecter ces règles pour garantir une bonne ambiance.",
                color=0x9b59b6
            )
            for titre, desc in RULES:
                embed.add_field(name=titre, value=desc, inline=False)
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(text="Le non-respect des règles peut entraîner des sanctions.")
            # Envoie l'embed avec le logo en pièce jointe
            try:
                # Vérifie si un message identique existe déjà
                async for msg in channel.history(limit=10):
                    if msg.author == self.bot.user and msg.embeds:
                        emb = msg.embeds[0]
                        if emb.title == embed.title and emb.description == embed.description:
                            return
                with open("img/anivers.png", "rb") as f:
                    file = discord.File(f, filename="anivers.png")
                    await channel.send(embed=embed, file=file)
            except Exception as e:
                print(f"Erreur envoi embed règles : {e}")

async def setup(bot):
    await bot.add_cog(Rule(bot))
