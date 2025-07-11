import discord
from discord.ext import commands

class LeaveMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_id = 1393293707842818269  # ID du salon de départ
        channel = member.guild.get_channel(channel_id)

        if channel:
            embed = discord.Embed(
                title="👋 Un membre nous quitte...",
                description=f"**{member.mention}** a quitté le serveur.",
                color=discord.Color.red()
            )
            embed.add_field(name="🪪 ID", value=member.id, inline=True)
            embed.add_field(name="📅 Date", value=discord.utils.format_dt(discord.utils.utcnow(), "F"), inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LeaveMessage(bot))
