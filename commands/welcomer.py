import discord
from discord.ext import commands

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = 1393285854159573143  # ID du salon de bienvenue
        role_id = 1393285704955465910     # ID du rôle à attribuer

        channel = member.guild.get_channel(channel_id)
        role = member.guild.get_role(role_id)

        if channel and role:
            await member.add_roles(role, reason="Nouveau membre")

            embed = discord.Embed(
                title="<:annieSmile:1393295476593266848> Bienvenue parmi nous !",  # Emoji custom ici
                description=f"{member.mention}, ravis de t’accueillir sur **{member.guild.name}** !\nLis les règles et amuse-toi bien ! 🍥",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text="Nouveau membre", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)

            await channel.send(
                content=member.mention,  # ping explicite
                embed=embed,
                allowed_mentions=discord.AllowedMentions(users=True)
            )

async def setup(bot):
    await bot.add_cog(Welcomer(bot))
