from discord.ext import commands
import discord
import json
import os

CONFIG_PATH = "config/honeypot_config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

class HoneypotMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 记录用户在蜜罐频道发过的消息内容
        self.user_messages = {}  # {user_id: set(message_content)}
    def get_all_banned_texts(self):
        all_texts = set()
        for user_id, texts in self.user_messages.items():
            all_texts.update(texts)
        return list(all_texts)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 跳过机器人
        if message.author.bot:
            return
        # 只处理公会消息
        if not message.guild:
            return
        # 动态加载配置
        config = load_config()
        # 找当前服务器配置
        entry = None
        for c in config:
            if str(message.guild.id) == c.get("guild_id"):
                entry = c
                break

        if not entry:
            # 没配置，跳过
            return

        honeypot_id = int(entry.get("honeypot_channel", 0))
        announcement_id = int(entry.get("announcement_channel", 0))
        whitelist = set(entry.get("whitelist_ids", []))

        author_id_str = str(message.author.id)

        # 如果作者在白名单，跳过处理
        if author_id_str in whitelist:
            # print(f"[INFO] 用户 {message.author} 在白名单，跳过")
            return

        # 服务器拥有者不删不封
        if message.author == message.guild.owner:
            # print("[INFO] 服务器拥有者，跳过处理")
            return

        # 检查bot权限和角色层级
        bot_member = message.guild.me
        if not bot_member.guild_permissions.manage_messages:
            print("[WARN] Bot缺少删除消息权限 manage_messages")
            return

        if not bot_member.guild_permissions.ban_members:
            print("[WARN] Bot缺少封禁成员权限 ban_members")

        if bot_member.top_role.position <= message.author.top_role.position:
            print(f"[WARN] Bot角色层级({bot_member.top_role.position})不高于用户({message.author.top_role.position})，无法执行封禁")

        # 1. 如果消息在蜜罐频道，记录内容，删消息，公告，封禁
        if message.channel.id == honeypot_id:
            # 记录消息内容
            user_set = self.user_messages.setdefault(message.author.id, set())
            user_set.add(message.content)

            # 删除消息
            try:
                await message.delete()
                print(f"[INFO] 删除蜜罐频道消息: {message.content} 来自 {message.author}")
            except Exception as e:
                print(f"[ERROR] 删除消息失败: {e}")

            # 发送违规公告
            await self._announce_violation(announcement_id, message.author, message.content)

            # 尝试封禁
            if bot_member.guild_permissions.ban_members and bot_member.top_role.position > message.author.top_role.position:
                try:
                    await message.guild.ban(message.author, reason="触发蜜罐频道违规")
                    print(f"[INFO] 封禁用户: {message.author} (ID: {message.author.id})")
                except Exception as e:
                    print(f"[ERROR] 封禁失败: {e}")
            else:
                print("[WARN] 不满足封禁权限或角色层级条件，跳过封禁")

            return  # 不再继续处理

        # 2. 非蜜罐频道消息，检查是否在蜜罐频道发过相同内容，删消息，公告，封禁
        if message.author.id in self.user_messages and message.content in self.user_messages[message.author.id]:
            # 删除消息
            try:
                await message.delete()
                print(f"[INFO] 删除非蜜罐频道重复消息: {message.content} 来自 {message.author}")
            except Exception as e:
                print(f"[ERROR] 删除消息失败: {e}")

            # 发送违规公告
            await self._announce_violation(announcement_id, message.author, message.content)

            # 封禁
            if bot_member.guild_permissions.ban_members and bot_member.top_role.position > message.author.top_role.position:
                try:
                    await message.guild.ban(message.author, reason="非蜜罐频道发送蜜罐消息")
                    print(f"[INFO] 封禁用户: {message.author} (ID: {message.author.id})")
                except Exception as e:
                    print(f"[ERROR] 封禁失败: {e}")
            else:
                print("[WARN] 不满足封禁权限或角色层级条件，跳过封禁")

            return

    async def _announce_violation(self, channel_id: int, user: discord.Member, content: str):
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"[WARN] 公告频道ID {channel_id} 未找到")
            return

        safe_content = content[:200].replace("`", "ˋ")
        try:
            await channel.send(
                f"⚠️ **Honeypot Triggered!**\n"
                f"👤 用户 {user.mention} 发送了违规信息\n"
                f"💬 消息内容：`{safe_content}`"
            )
            print("[INFO] 已在公告频道发送违规通知")
        except Exception as e:
            print(f"[ERROR] 发送公告失败: {e}")

async def setup(bot):
    await bot.add_cog(HoneypotMonitor(bot))