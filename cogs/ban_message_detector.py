import discord
from discord.ext import commands
import json
import os

BAN_MESSAGE_FILE = "config/ban_message.json"

def load_ban_config():
    if not os.path.exists(BAN_MESSAGE_FILE):
        return {"ban_words": [], "whitelist_channels": [], "log_channel_id": None}
    try:
        with open(BAN_MESSAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"ban_words": [], "whitelist_channels": [], "log_channel_id": None}

class BanMessageDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_bad_word(self, content, ban_words):
        for word in ban_words:
            if word in content:
                return word
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        config = load_ban_config()
        ban_words = config.get("ban_words", [])
        whitelist = config.get("whitelist_channels", [])
        log_channel_id = config.get("log_channel_id")

        if message.channel.id in whitelist:
            return

        bad_word = self.check_bad_word(message.content, ban_words)
        if bad_word:
            try:
                await message.delete()
            except Exception:
                pass

            try:
                await message.author.send(f"你触发了违规词：`{bad_word}`，消息已被删除。")
            except Exception:
                pass

            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(
                        f"用户 {message.author} (ID: {message.author.id}) 在频道 {message.channel.mention} "
                        f"发送了违规词 `{bad_word}` 的消息：\n{message.content}"
                    )

async def setup(bot):
    await bot.add_cog(BanMessageDetector(bot))
