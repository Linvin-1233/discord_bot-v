import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import asyncio

print("当前工作目录:", os.getcwd())
print("ban_message.json 绝对路径:", os.path.abspath("config/ban_message.json"))

load_dotenv(dotenv_path="token.env")
token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

with open("config/honeypot_config.json", "r") as f:
    honeypot_config = json.load(f)

bot.honeypots = honeypot_config

TEST_GUILD_ID = 1399108525954957442

@bot.event
async def on_ready():
    guild = discord.Object(id=1399108525954957442)  # 替换成你测试的服务器ID，int类型
    await bot.tree.sync(guild=guild)
    print(f"✅ Slash 命令已同步到服务器，Bot 在线：{bot.user}")

async def main():
    await bot.load_extension("cogs.honeypot_monitor")
    await bot.load_extension("cogs.ban_message_detector")
    await bot.load_extension("cogs.text_triggers")
    await bot.load_extension("cogs.config_commands")
    await bot.load_extension("cogs.people_counting")
    await bot.load_extension("cogs.welcome_listener")
    await bot.load_extension("cogs.cog_load")
    await bot.start(token)

asyncio.run(main())