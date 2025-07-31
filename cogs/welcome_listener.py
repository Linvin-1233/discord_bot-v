import discord
from discord.ext import commands
import json
import os

WELCOME_FILE = "config/welcome_message.json"

def load_welcome_config():
    if not os.path.exists(WELCOME_FILE):
        return {}
    try:
        with open(WELCOME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

class WelcomeListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = load_welcome_config()
        guild_id = str(member.guild.id)

        if guild_id not in data:
            return

        channel_id = int(data[guild_id]["channel_id"])
        message = data[guild_id]["message"]
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        # 計算伺服器成員數（含機器人）
        count = len(member.guild.members)

        embed = discord.Embed(
            title=f"🎉 歡迎 {member.mention} 加入 {member.guild.name}",
            description=f"{message}\n\n你是第 **{count}** 個加入的成員！",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeListener(bot))