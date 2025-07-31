import discord
from discord.ext import commands
import json
import os

# 關鍵字對應回覆
CONFIG_PATH = "config/auto_reply.json"

def load_triggers():
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_triggers(trigger_list):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(trigger_list, f, ensure_ascii=False, indent=2)

def find_reply(keyword, triggers):
    for item in triggers:
        if item.get("keyword") == keyword:
            return item.get("reply")
    return None

class TextTriggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keyword_triggers = load_triggers()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.strip()
        reply = find_reply(content, self.keyword_triggers)
        if reply:
            await message.channel.send(reply)
            print(f"[关键词触发] {message.author}：{content}")

async def setup(bot):
    await bot.add_cog(TextTriggers(bot))