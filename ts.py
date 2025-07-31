import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv("token.env")
token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1399108525954957442  # 服务器ID，整数

@bot.event
async def on_ready():
    print(f"Bot 已上线: {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"无法找到服务器ID {GUILD_ID}")
        await bot.close()
        return

    commands = await bot.tree.fetch_commands(guild=guild)
    if not commands:
        print("这个服务器没有注册任何 Slash 命令。")
    else:
        print(f"服务器 {guild.name} 已注册的 Slash 命令列表：")
        for cmd in commands:
            print(f"- {cmd.name}: {cmd.description}")

    await bot.close()

print(os.getcwd())
print(os.path.abspath("../config/auto_reply.json"))

bot.run(token)
