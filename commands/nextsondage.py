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
        self.sondage_hour = 22 # Heure de publication (24h)
        self.sondage_minute = 0 + 1  # Minute de publication
        self.next_run = None
        self.already_sent_today = False  # Flag pour éviter doublons
        self.send_sondage_task.start()

    def cog_unload(self):
        self.send_sondage_task.cancel()

    @tasks.loop(seconds=30)  # on check toutes les 30 secondes pour être plus réactif
    async def send_sondage_task(self):
        now = datetime.datetime.now()
        target = now.replace(hour=self.sondage_hour, minute=self.sondage_minute, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)

        diff = (target - now).total_seconds()

        # Envoi du sondage si on est dans la minute cible et pas déjà envoyé aujourd’hui
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

                # Ajout des réactions emoji
                for option in sondage['options']:
                    try:
                        print(f"Ajout de la réaction {option['emoji']}")
                        await msg.add_reaction(option['emoji'])
                    except discord.errors.HTTPException as e:
                        print(f"Erreur ajout réaction {option['emoji']} : {e}")

                await self.mark_sondage_posted(sondage['id'])
                self.already_sent_today = True
                self.next_run = target + datetime.timedelta(days=1)

        # Reset flag dès qu’on passe la minute cible
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
