import discord
from discord.ext import commands
import asyncio
import os

# Lire le token depuis token.txt
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Synchronisation slash commands
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# Chargement automatique des commandes
async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            module = f"commands.{filename[:-3]}"
            try:
                await bot.load_extension(module)
                print(f"✅ Module chargé : {module}")
            except Exception as e:
                print(f"❌ Erreur chargement {module} : {e}")

# Lancement du bot
async def main():
    await load_extensions()
    await bot.start(TOKEN)

asyncio.run(main())
