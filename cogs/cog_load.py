import discord
from discord.ext import commands
import json, os

from cogs.ticket_system import TicketControlView, TicketOpenButton

TICKET_FILE = "config/ticket.json"

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class CogLoad(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._restored = False  # 避免多次重綁

    @commands.Cog.listener()
    async def on_ready(self):
        if self._restored:
            return

        print("[INFO] Bot 已上線，開始重綁客服單面板與控制按鈕...")
        ticket_data = load_json(TICKET_FILE)
        restored_count = 0
        changed = False  # 紀錄是否有刪除無效紀錄

        for guild_id, info in list(ticket_data.items()):
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                print(f"[CLEANUP] 找不到伺服器 {guild_id}，刪除整個紀錄")
                ticket_data.pop(guild_id)
                changed = True
                continue

            #重綁客服單面板按鈕
            for panel in info.get("panels", [])[:]:  # 複製列表以便刪除
                channel = self.bot.get_channel(panel["channel_id"])
                if not channel:
                    print(f"[CLEANUP] 找不到頻道 {panel['channel_id']}，刪除面板紀錄")
                    info["panels"].remove(panel)
                    changed = True
                    continue
                try:
                    msg = await channel.fetch_message(panel["message_id"])
                    await msg.edit(view=TicketOpenButton(self.bot, panel.get("reason", "開單")))
                    print(f"[INFO] 已重綁開單面板：{channel.name}")
                    restored_count += 1
                except discord.NotFound:
                    print(f"[CLEANUP] 找不到面板訊息 {panel['message_id']}，刪除紀錄")
                    info["panels"].remove(panel)
                    changed = True
                except Exception as e:
                    print(f"[WARNING] 重綁面板失敗 {panel['message_id']}: {e}")
                    info["panels"].remove(panel)
                    changed = True

            #重綁客服單控制面板
            for ticket in info.get("tickets", [])[:]:
                if not ticket.get("active"):
                    continue
                channel = self.bot.get_channel(ticket["channel_id"])
                user = self.bot.get_user(ticket["user_id"])
                if not channel or not user:
                    print(f"[CLEANUP] 找不到客服單頻道或用戶，刪除紀錄")
                    info["tickets"].remove(ticket)
                    changed = True
                    continue
                try:
                    msg = await channel.fetch_message(ticket["message_id"])
                    await msg.edit(view=TicketControlView(channel, user))
                    print(f"[INFO] 已重綁控制按鈕：{channel.name}")
                    restored_count += 1
                except discord.NotFound:
                    print(f"[CLEANUP] 找不到控制訊息 {ticket['message_id']}，刪除紀錄")
                    info["tickets"].remove(ticket)
                    changed = True
                except Exception as e:
                    print(f"[WARNING] 重綁控制失敗 {ticket['message_id']}: {e}")
                    info["tickets"].remove(ticket)
                    changed = True

        # 如果有刪除紀錄則保存
        if changed:
            save_json(TICKET_FILE, ticket_data)
            print("[INFO] 已清理無效紀錄並保存 JSON")

        print(f"[INFO] 重綁完成，共恢復 {restored_count} 個按鈕。")
        self._restored = True

async def setup(bot: commands.Bot):
    await bot.add_cog(CogLoad(bot))