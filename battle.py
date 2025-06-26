import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

from data import coins, save_coins, equipped_items, all_items, get_item_power

def setup(bot: commands.Bot):
    @bot.tree.command(name="battle", description="他のプレイヤーとナエンをかけて対戦するなえ！")
    @app_commands.describe(opponent="対戦相手", bet="かけるナエンの量（省略時は0）")
    async def battle(interaction: discord.Interaction, opponent: discord.Member, bet: int = 0):
        challenger_id = str(interaction.user.id)
        opponent_id = str(opponent.id)

        # 自分とのバトルは不可
        if challenger_id == opponent_id:
            await interaction.response.send_message("❌ 自分とは戦えないなえ！", ephemeral=True)
            return

        # ナエンチェック（所持金がない場合初期化）
        coins.setdefault(challenger_id, 1000)
        coins.setdefault(opponent_id, 1000)

        if coins[challenger_id] < bet:
            await interaction.response.send_message(f"❌ あなたのナエンが足りないなえ！（所持：{coins[challenger_id]}）", ephemeral=True)
            return
        if coins[opponent_id] < bet:
            await interaction.response.send_message(f"❌ 相手のナエンが足りないなえ！（所持：{coins[opponent_id]}）", ephemeral=True)
            return

        # 同意の確認
        await interaction.response.send_message(
            f"{opponent.mention} さん、{interaction.user.mention} から **{bet}ナエン** をかけた対戦の申し込みがあるなえ！\n"
            f"30秒以内に「✅」で承諾、または何もしなければキャンセルされるなえ！",
            ephemeral=False
        )
        prompt_msg = await interaction.original_response()
        await prompt_msg.add_reaction("✅")

        def check_reaction(reaction, user):
            return (
                user == opponent and
                str(reaction.emoji) == "✅" and
                reaction.message.id == prompt_msg.id
            )

        try:
            await bot.wait_for("reaction_add", timeout=30.0, check=check_reaction)
        except asyncio.TimeoutError:
            await interaction.followup.send("⌛ 対戦はキャンセルされたなえ。", ephemeral=False)
            return

        # 戦闘ロジック
        def get_power(user_id):
            equipped = equipped_items.get(user_id)
            if equipped and equipped in all_items:
                return all_items[equipped].get("power", 0)
            return 0

        challenger_power = get_power(challenger_id)
        opponent_power = get_power(opponent_id)

        total_power = challenger_power + opponent_power
        if total_power == 0:
            winner_id = random.choice([challenger_id, opponent_id])
        else:
            prob_challenger = challenger_power / total_power
            winner_id = challenger_id if random.random() < prob_challenger else opponent_id

        # 勝敗処理
        if bet > 0:
            coins[challenger_id] -= bet
            coins[opponent_id] -= bet
            coins[winner_id] += bet * 2
            save_coins()

        winner = interaction.user if winner_id == challenger_id else opponent
        loser = opponent if winner_id == challenger_id else interaction.user

        await interaction.followup.send(
            f"⚔️ {interaction.user.mention} vs {opponent.mention} の対戦結果なえ！\n"
            f"🏆 勝者：{winner.mention}\n"
            f"💸 {bet * 2}ナエンをゲット！" if bet > 0 else f"🎮 フレンドリーマッチだったなえ！"
        )
