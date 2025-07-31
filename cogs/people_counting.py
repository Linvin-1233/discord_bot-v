import discord
from discord.ext import commands
from cogs.config_commands import load_all_counts, save_count
import json

class PeopleCounting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_channel_id(self, guild_id: int):
        data = load_all_counts()
        return data.get(str(guild_id), {}).get("channel_id")

    async def update_channel_name(self, guild: discord.Guild):
        channel_id = self.get_channel_id(guild.id)
        if not channel_id:
            return

        channel = guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        member_count = guild.member_count
        try:
            await channel.edit(name=f"人數-{member_count}")
            save_count(guild.id, channel.id, member_count)
        except Exception as e:
            print(f"❌ 更新人數頻道失敗: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.update_channel_name(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.update_channel_name(member.guild)

async def setup(bot):
    await bot.add_cog(PeopleCounting(bot))