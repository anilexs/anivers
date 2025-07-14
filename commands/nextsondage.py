# a ajoute une allert si il a pas de sondage pour le landemain sur un salon

import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
import datetime
from datetime import timedelta

ROLE_ID = 1392955504338407434  # ID du rôle à mentionner
SONDAGE_CHANNEL_ID = 1392955777643446312  # ID du salon pour poster


class SondageScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sondage_hour = 10  # Heure de publication (24h)
        self.sondage_minute = 10 + 1  # Minute de publication
        self.next_run = None
        self.already_sent_today = False
        self.send_sondage_task.start()

    def cog_unload(self):
        self.send_sondage_task.cancel()

    # ✅ Limiter à UNE réaction par utilisateur
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != SONDAGE_CHANNEL_ID:
            return

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            print(f"[DEBUG] Erreur fetch message: {e}")
            return

        if not message.author or message.author.id != self.bot.user.id:
            return

        # Supprimer toutes les autres réactions du même utilisateur
        for reaction in message.reactions:
            if str(reaction.emoji) != str(payload.emoji):
                try:
                    await message.remove_reaction(reaction.emoji, discord.Object(id=payload.user_id))
                    print(f"[DEBUG] Suppression de la réaction {reaction.emoji} pour user {payload.user_id}")
                except Exception as e:
                    print(f"[DEBUG] Erreur suppression réaction: {e}")

    @tasks.loop(seconds=30)
    async def send_sondage_task(self):
        now = datetime.datetime.now()
        target = now.replace(hour=self.sondage_hour, minute=self.sondage_minute, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)

        diff = (target - now).total_seconds()

        if diff <= 60 and not self.already_sent_today:
            print(f"[DEBUG] Envoi sondage à {now.strftime('%H:%M:%S')}")

            channel = self.bot.get_channel(SONDAGE_CHANNEL_ID)
            if not channel:
                print("Salon sondage introuvable")
                return

            sondage = await self.get_next_sondage()
            if sondage:
                role = channel.guild.get_role(ROLE_ID)
                role_mention = role.mention if role else ""
                options_text = "\n".join([f"{opt['emoji']} {opt['text']}" for opt in sondage['options']])
                msg = await channel.send(f"{role_mention} 📢 Nouveau sondage du jour :\n**{sondage['question']}**\n\n{options_text}")

                for option in sondage['options']:
                    try:
                        await msg.add_reaction(option['emoji'])
                    except discord.errors.HTTPException as e:
                        print(f"Erreur ajout réaction {option['emoji']} : {e}")

                await self.mark_sondage_posted(sondage['id'])
                self.already_sent_today = True
                self.next_run = target + datetime.timedelta(days=1)

        if diff > 60 and self.already_sent_today:
            self.already_sent_today = False

    @send_sondage_task.before_loop
    async def before_send_sondage(self):
        await self.bot.wait_until_ready()

    async def get_next_sondage(self):
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, options, emojis FROM sondage WHERE posted = 0 ORDER BY id ASC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            id, question, options_str, emojis_str = row
            options = options_str.split('%')
            emojis = [e.replace('\\', '') for e in emojis_str.split('%')]
            return {
                'id': id,
                'question': question,
                'options': [
                    {'text': opt, 'emoji': emoji}
                    for opt, emoji in zip(options, emojis)
                ]
            }
        except Exception as e:
            print(f"Erreur lecture sondages: {e}")
            return None

    async def mark_sondage_posted(self, sondage_id):
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE sondage SET posted = 1 WHERE id = ?", (sondage_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur mise à jour sondage : {e}")

    @app_commands.command(name="tempsrestant", description="Affiche le temps restant avant le prochain sondage")
    async def tempsrestant(self, interaction: discord.Interaction):
        now = datetime.datetime.now()
        if self.next_run is None:
            target = now.replace(hour=self.sondage_hour, minute=self.sondage_minute, second=0, microsecond=0)
            if now >= target:
                target += datetime.timedelta(days=1)
            self.next_run = target
        diff = self.next_run - now
        heures, reste = divmod(diff.seconds, 3600)
        minutes = reste // 60
        await interaction.response.send_message(f"⏳ Prochain sondage dans {heures}h {minutes}min.")

    @app_commands.command(name="nextsondage", description="Affiche l'heure exacte et la date du prochain sondage")
    async def nextsondage(self, interaction: discord.Interaction):
        now = datetime.datetime.now()
        target = now.replace(hour=self.sondage_hour, minute=self.sondage_minute, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)
        heure_moins_une = target - timedelta(minutes=1)
        await interaction.response.send_message(
            f"📅 Prochain sondage prévu à : **{heure_moins_une.strftime('%H:%M')}** le {heure_moins_une.strftime('%d/%m/%Y')}"
        )


async def setup(bot):
    await bot.add_cog(SondageScheduler(bot))