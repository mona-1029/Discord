import os
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"{bot.user} でログインしました")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "ポモドーロ":
        await message.channel.send("🍅 ポモドーロBot準備中")

    await bot.process_commands(message)

bot.run(TOKEN)