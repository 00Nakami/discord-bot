import discord
from discord import app_commands
from discord.ext import commands
from data import items, equipped, save_equipped, all_items

class Equip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="equip", description="持っているアイテムを装備するなえ！")
    @app_commands.describe(item_name="装備するアイテムの名前")
    async def equip(self, interaction: discord.Interaction, item_name: str):
        user_id = str(interaction.user.id)

        # 入手済みチェック
        if user_id not in items or item_name not in items[user_id] or items[user_id][item_name] <= 0:
            await interaction.response.send_message(f"❌ 「{item_name}」 を持ってないなえ！", ephemeral=True)
            return

        # アイテム存在チェック
        if item_name not in all_items:
            await interaction.response.send_message(f"❌ 「{item_name}」 というアイテムは存在しないなえ！", ephemeral=True)
            return

        # 装備処理
        equipped[user_id] = item_name
        save_equipped()

        await interaction.response.send_message(
            f"🛡️ {interaction.user.mention} さんは「**{item_name}**」を装備したなえ！",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Equip(bot))
