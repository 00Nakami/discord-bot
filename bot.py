from keep_alive import keep_alive
keep_alive()

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from discord import Embed, Interaction
import random
import json
import os
from dotenv import load_dotenv
import asyncio
from data import all_items, rarity_info  # ← これで使えるようになる

# --- 環境変数読み込み ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKENが.envに設定されていません")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# --- ファイルパス ---
STATS_FILE = "stats.json"
COINS_FILE = "coins.json"
ITEMS_FILE = "items.json"

# --- グローバル変数 ---
stats = {}
coins = {}

# --- 定数 ---
JANKEN_CHOICES = ["ぐー", "ちょき", "ぱー"]

# --- ファイル操作 ---

def load_stats():
    global stats
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 不足キー補填
            for user_id, s in data.items():
                s.setdefault("streak", 0)
                s.setdefault("max_streak", 0)
                s.setdefault("lose_streak", 0)
                s.setdefault("max_lose_streak", 0)
                s.setdefault("draw_streak", 0)
                s.setdefault("max_draw_streak", 0)
            stats = data
    else:
        stats = {}

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def load_coins():
    global coins
    if os.path.exists(COINS_FILE):
        with open(COINS_FILE, "r", encoding="utf-8") as f:
            coins = json.load(f)
    else:
        coins = {}

def save_coins():
    with open(COINS_FILE, "w", encoding="utf-8") as f:
        json.dump(coins, f, ensure_ascii=False, indent=2)

def load_items():
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_items(data):
    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

items = load_items()  # bot起動時に読み込む（グローバル変数として）

def add_item_to_user(user_id: str, item_name: str, count: int = 1):
    if user_id not in items:
        items[user_id] = {}
    if item_name in items[user_id]:
        items[user_id][item_name] += count
    else:
        items[user_id][item_name] = count
    save_items(items)

load_stats()
load_coins()

# --- ユーティリティ関数 ---

def judge(user_hand, bot_hand):
    """じゃんけんの勝敗判定"""
    # グー:0, チョキ:1, パー:2 のルールで計算
    mapping = {"ぐー":0, "ちょき":1, "ぱー":2}
    user = mapping[user_hand]
    bot_ = mapping[bot_hand]
    if user == bot_:
        return "draw"
    elif (user - bot_) % 3 == 1:
        return "win"
    else:
        return "lose"

def initialize_user_stats(user_id: str):
    if user_id not in stats:
        stats[user_id] = {
            "win": 0, "lose": 0, "draw": 0,
            "streak": 0, "max_streak": 0,
            "lose_streak": 0, "max_lose_streak": 0,
            "draw_streak": 0, "max_draw_streak": 0,
        }

def initialize_user_coins(user_id: str):
    if user_id not in coins:
        coins[user_id] = 1000

# --- Bot起動時 ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ ログイン完了: {bot.user}")
    print("✅ スラッシュコマンド同期済み")

# ====== じゃんけん ======

@bot.tree.command(name="janken", description="じゃんけんするなえ！（ぐー・ちょき・ぱー）")
@app_commands.describe(
    hand="あなたの手を選んでください",
    bet="ベットするナエンの数（100〜10000）"
)
@app_commands.choices(hand=[
    app_commands.Choice(name="ぐー ✊", value="ぐー"),
    app_commands.Choice(name="ちょき ✌️", value="ちょき"),
    app_commands.Choice(name="ぱー ✋", value="ぱー")
])
async def janken(interaction: discord.Interaction, hand: app_commands.Choice[str], bet: int):
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    user_id = str(interaction.user.id)
    user_hand = hand.value
    bot_hand = random.choice(JANKEN_CHOICES)
    result = judge(user_hand, bot_hand)

    if bet < 100 or bet > 10000:
        await interaction.followup.send("❌ ベットは100〜10000ナエンの範囲で指定してなえ！", ephemeral=True)
        return

    initialize_user_stats(user_id)
    initialize_user_coins(user_id)

    if coins[user_id] < bet:
        await interaction.followup.send(f"❌ ナエンが足りないなえ！現在の所持: {coins[user_id]}ナエン", ephemeral=True)
        return

    coins[user_id] -= bet

    # 結果を記録
    stats[user_id][result] += 1

    BOT_QUOTES = {
        "lose": [
            "よゆなえでくさなえꉂ🤭",
            "これはよゆなえこえてなーじーꉂ🤭",
            "いーじーなーじーやなー、"
        ],
        "draw": [
            "つぎはぼこなえにしてやるかーꉂ🤭",
            "ぼこなえにしてやるかー、",
            "引きなえかなー、"
        ]
    }

    def get_win_quote(streak):
        if streak >= 5:
            return random.choice([
                f"{streak}連勝とかやばなえすぎやは！",
                "チートナイスーꉂ🤭",
                "絶対チートやんけ！"
            ])
        elif streak >= 3:
            return random.choice([
                f"{streak}連勝はやばなえ",
                "ずるしてるやんけ！",
                "わざと負けてあげましたꉂ🤭"
            ])
        else:
            return random.choice([
                "なんでこれで負けるねん！",
                "手加減してあげてたんよな〜ꉂ🤭",
                "たまたま勝ってなんやねん"
            ])

    # 連勝等の処理＋報酬計算
    if result == "win":
        stats[user_id]["streak"] += 1
        stats[user_id]["max_streak"] = max(stats[user_id]["max_streak"], stats[user_id]["streak"])
        stats[user_id]["lose_streak"] = 0
        stats[user_id]["draw_streak"] = 0
        multiplier = 2 ** stats[user_id]["streak"]
        reward = bet * multiplier
        bot_comment = get_win_quote(stats[user_id]["streak"])
    elif result == "draw":
        stats[user_id]["draw_streak"] += 1
        stats[user_id]["max_draw_streak"] = max(stats[user_id]["max_draw_streak"], stats[user_id]["draw_streak"])
        stats[user_id]["streak"] = 0
        stats[user_id]["lose_streak"] = 0
        reward = bet
        bot_comment = random.choice(BOT_QUOTES["draw"])
    else:
        stats[user_id]["lose_streak"] += 1
        stats[user_id]["max_lose_streak"] = max(stats[user_id]["max_lose_streak"], stats[user_id]["lose_streak"])
        stats[user_id]["streak"] = 0
        stats[user_id]["draw_streak"] = 0
        reward = int(bet * 0.5)
        bot_comment = random.choice(BOT_QUOTES["lose"])

    coins[user_id] += reward
    save_stats()
    save_coins()

    result_text = {
        "win": "あなたの勝ち！ 🎉",
        "lose": "あなたの負け… 💔",
        "draw": "あいこ！ 🤝"
    }

    await interaction.followup.send(
        f"🧍‍♂️ あなたの手: {user_hand}\n"
        f"🐧 なえくんBotの手: {bot_hand}\n"
        f"🎲 結果: {result_text[result]}\n"
        f"💰 ベット: {bet}ナエン\n"
        f"🎁 獲得ナエン: {reward}ナエン\n"
        f"🔥 現在の連勝数: {stats[user_id]['streak']}回\n"
        f"🪙 現在の所持ナエン: {coins[user_id]}ナエン\n"
        f"💬 なえくんBot: {bot_comment}"
    )

@bot.tree.command(name="janken_stats", description="あなたのじゃんけん戦績を表示します")
async def janken_stats(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    user_id = str(interaction.user.id)
    user_stats = stats.get(user_id, {
        "win": 0, "lose": 0, "draw": 0,
        "streak": 0, "max_streak": 0,
        "lose_streak": 0, "max_lose_streak": 0,
        "draw_streak": 0, "max_draw_streak": 0,
    })
    total = user_stats["win"] + user_stats["lose"] + user_stats["draw"]

    if total == 0:
        await interaction.followup.send("📊 まだ対戦履歴がありません！ `/janken` で遊んでみよう！")
        return

    win_rate = (user_stats["win"] / (user_stats["win"] + user_stats["lose"]) * 100) if (user_stats["win"] + user_stats["lose"]) > 0 else 0.0

    await interaction.followup.send(
        f"📊 **{interaction.user.name}さんのじゃんけん戦績**\n"
        f"✅ 勝ち: {user_stats['win']}回\n"
        f"❌ 負け: {user_stats['lose']}回\n"
        f"🤝 あいこ: {user_stats['draw']}回\n"
        f"🔥 現在の連勝数: {user_stats['streak']}回\n"
        f"🏆 最高連勝数: {user_stats['max_streak']}回\n"
        f"☠️ 最高連敗数: {user_stats['max_lose_streak']}回\n"
        f"🤝 最高連続あいこ数: {user_stats['max_draw_streak']}回\n"
        f"🎯 勝率: {win_rate:.1f}%（全{total}回）"
    )

@bot.tree.command(name="janken_ranking", description="じゃんけんのランキングを表示するなえ！")
async def janken_ranking(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
    except discord.errors.InteractionResponded:
        pass

    ranked_stats = []
    for user_id, s in stats.items():
        ranked_stats.append({
            "id": user_id,
            "win": s.get("win", 0),
            "max_streak": s.get("max_streak", 0),
            "max_lose_streak": s.get("max_lose_streak", 0),
            "max_draw_streak": s.get("max_draw_streak", 0),
        })

    async def format_ranking(title, key):
        sorted_list = sorted(ranked_stats, key=lambda x: x[key], reverse=True)[:3]
        if not sorted_list:
            return f"**{title}**\n（データがありません）"
        lines = [f"**{title}**"]
        for i, entry in enumerate(sorted_list, 1):
            try:
                user = await bot.fetch_user(int(entry["id"]))
                value = entry[key]
                lines.append(f"{i}. {user.name} - {value}回")
            except Exception:
                continue
        return "\n".join(lines)

    win_ranking = await format_ranking("🏆 勝利数ランキング", "win")
    streak_ranking = await format_ranking("🔥 最高連勝ランキング", "max_streak")
    lose_ranking = await format_ranking("☠️ 最高連敗ランキング", "max_lose_streak")
    draw_ranking = await format_ranking("🤝 最高連続あいこランキング", "max_draw_streak")

    await interaction.followup.send(
        f"{win_ranking}\n\n{streak_ranking}\n\n{lose_ranking}\n\n{draw_ranking}"
    )

# ====== おみくじ ======

@bot.tree.command(name="naemikuji", description="なえみくじ引いて行くなえ？（1回100ナエン）")
async def omikuji(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    user_id = str(interaction.user.id)
    initialize_user_coins(user_id)

    if coins[user_id] < 100:
        await interaction.followup.send(f"❌ ナエンが足りないなえ！現在の所持: {coins[user_id]}ナエン", ephemeral=True)
        return

    coins[user_id] -= 100

    results = ["大苗 🎉", "中苗 😊", "苗 🙂", "小苗 😌", "末苗 😐", "狐 😢", "大狐 😱"]
    choice = random.choice(results)

    if choice.startswith("大苗"):
        reward = 1000
    elif choice.startswith("中苗"):
        reward = 200
    elif choice.startswith("狐") and not choice.startswith("大狐"):
        reward = 50
    elif choice.startswith("大狐"):
        reward = 0
    else:
        reward = 100

    coins[user_id] += reward
    save_coins()

    await interaction.followup.send(
        f"🎋 {interaction.user.mention} さんのなえみくじ結果は **{choice}** なえ〜\n"
        f"💰 手数料: 100ナエン\n"
        f"🎁 獲得ナエン: {reward}ナエン\n"
        f"🪙 現在の所持ナエン: {coins[user_id]}ナエン"
    )

# ====== Bedwarskit ======

@bot.tree.command(name="bedwarskit", description="なえくんがおすすめのキットを言うなえ！")
async def bedwarskit(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    kits = [
        "ノーキット", "ランダム", "アデトゥンデ", "アグニ", "サンショウウオのエーミーさん", "ベグザット",
        "サイバー", "へファイストス", "灼熱のシールダー", "クリスタル", "リアン", "ルーメンちゃん",
        "メロディ", "Nahla", "海賊のデイビー", "スティクス", "タリヤ", "トリクシー", "ウマ",
        "ヴァネッサ", "虚空の騎士", "ささやき", "レン", "ゼノ（魔法使い）", "ベイカー", "ヤバン人",
        "ルシア", "ナザール", "イザベル", "マルセル", "マーティン", "ラグナー", "Ramil", "アラクネ",
        "エンバー", "アーチャー", "ビルダー", "遺体安置所", "デス・アダー", "エルダー・ツリー",
        "エルドリック", "エベリン", "農家のクリタス", "フレーヤ", "死神", "グローブ", "ハンナ",
        "カイダ", "ラシー", "ライラ", "マリーナ", "ミロ", "マイナー", "シェイラ", "シグリッド",
        "サイラス", "スコル", "トリニティ", "トライトン", "ヴォイドリージェント", "バルカン",
        "ユジ", "ゼニス", "エアリー", "錬金術師", "アレース", "養蜂家のビートリックスさん", "賞金稼ぎ",
        "ケイトリン", "コバルト", "コグスワース", "征服者", "ワニオオカミ", "きょうりゅう手なずけ師のドム",
        "ドリル", "エレクトラ", "漁師", "フローラ", "フォルトゥナ", "フロスティ", "ジンジャーブレッドマン",
        "ゴンビイさん", "イグニス", "ジャック", "ジェイド", "カライヤちゃん", "ラニ", "商人のマルコさん",
        "メタルディテクターさん", "ノエル", "ニョカ", "ニュクス", "パイロキネシス", "からす", "サンタ",
        "羊飼い", "スモーク", "スピリットキャッチャーさん", "スターコレクターのステラちゃん", "テラ",
        "トラッパー", "ウンブラ", "梅子", "ウォーデン", "戦士", "ウィムさん", "シューロット", "ヤミニ",
        "イエティ", "ゼファー"
    ]
    choice = random.choice(kits)
    await interaction.followup.send(f"💯 {interaction.user.mention} さんにおすすめのキットは **{choice}** なえ〜！")

# ====== 計算コマンド ======

@bot.tree.command(name="sansuu", description="整数の計算をするなえ！")
@app_commands.describe(
    a="整数1つ目なえ",
    b="整数2つ目なえ",
    op="演算子を選ぶなえ〜"
)
@app_commands.choices(op=[
    app_commands.Choice(name="足し算（+）", value="+"),
    app_commands.Choice(name="引き算（-）", value="-"),
    app_commands.Choice(name="掛け算（×）", value="×"),
    app_commands.Choice(name="割り算（÷）", value="÷"),
])
async def calc(interaction: discord.Interaction, a: int, b: int, op: app_commands.Choice[str]):
    try:
        await interaction.response.defer()
    except discord.errors.InteractionResponded:
        pass

    user_id = str(interaction.user.id)
    if user_id not in coins:
        coins[user_id] = 1000  # 初期ナエン

    try:
        if op.value == "+":
            res = a + b
        elif op.value == "-":
            res = a - b
        elif op.value == "×":
            res = a * b
        elif op.value == "÷":
            if b == 0:
                await interaction.followup.send("❌ 0で割るのはできなえ！")
                return
            quotient = a // b
            remainder = a % b
            await interaction.followup.send(f"{a} ÷ {b} = {quotient} あまり {remainder}")
            # 計算成功として100ナエン付与
            coins[user_id] += 100
            save_coins()
            return
        else:
            await interaction.followup.send("❌ 不正な演算子なえ！")
            return
    except Exception as e:
        await interaction.followup.send(f"❌ エラーが発生したなえ: {e}")
        return

    # 成功時に100ナエン付与
    coins[user_id] += 100
    save_coins()

    await interaction.followup.send(f"{a} {op.value} {b} = {res}\n🎉 計算成功で100ナエン獲得！ 現在の所持ナエン: {coins[user_id]}ナエンなえ！")

# ====== スロット（ベット機能付き） ======

class SlotView(View):
    def __init__(self, user, bet):
        super().__init__(timeout=60)
        self.emojis = ["🐧", "🍒", "🔔", "🦊", "🐟", "😹"]
        self.running = False
        self.message = None
        self.user = user
        self.bet = bet

    async def slot_animation(self, interaction: Interaction):
        self.running = True
        final_slots = [None, None, None]
        slots = [random.choice(self.emojis) for _ in range(3)]

        embed = Embed(title="スロットマシン", description="🎰 回転中...", color=discord.Color.gold())
        embed.add_field(name="結果", value=" ".join(slots), inline=False)

        if self.message is None:
            self.message = await interaction.original_response()

        for stop_index in range(3):
            for _ in range(10):
                for i in range(3):
                    if i <= stop_index:
                        if final_slots[i] is None:
                            final_slots[i] = random.choice(self.emojis)
                        slots[i] = final_slots[i]
                    else:
                        slots[i] = random.choice(self.emojis)

                embed.set_field_at(0, name="結果", value=" ".join(slots), inline=False)
                await self.message.edit(embed=embed, view=self)
                await asyncio.sleep(0.02)

        user_id = str(self.user.id)
        user_coins = coins.get(user_id, 1000)

        # 結果判定と配当
        if final_slots[0] == final_slots[1] == final_slots[2]:
            winnings = self.bet * 3
            coins[user_id] = user_coins + winnings
            result_msg = f"🎉 大当たり！ {''.join(final_slots)} が揃ったなえ！\n💰 {winnings}ナエン獲得！"
        elif final_slots[0] == final_slots[1] or final_slots[1] == final_slots[2] or final_slots[0] == final_slots[2]:
            winnings = int(self.bet * 1.5)
            coins[user_id] = user_coins + winnings
            result_msg = f"🙂 小当たり！ {''.join(final_slots)} のペアが揃ったなえ！\n💰 {winnings}ナエン獲得！"
        else:
            winnings = 0
            result_msg = f"😢 残念！ {''.join(final_slots)} はハズレなえ…\n💰 0ナエン"

        save_coins()

        embed.description = result_msg + f"\n🎉 現在の所持金: {coins[user_id]}ナエン"
        await self.message.edit(embed=embed, view=None)
        self.running = False

    @discord.ui.button(label="回す", style=discord.ButtonStyle.green)
    async def spin(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("⚠️ これはあなたのスロットじゃないなえ！", ephemeral=True)
            return

        if self.running:
            await interaction.response.send_message("⚠️ もう回ってるなえ！少しまってなえ！", ephemeral=True)
            return

        await interaction.response.defer()
        await self.slot_animation(interaction)

@bot.tree.command(name="slot", description="スロットを回すなえ！")
@app_commands.describe(bet="ベットするナエンの量なえ")
async def slot(interaction: Interaction, bet: int):
    user_id = str(interaction.user.id)
    if bet <= 0:
        await interaction.response.send_message("❌ ベットは1以上の整数で指定してなえ！", ephemeral=True)
        return

    user_coins = coins.get(user_id, 1000)
    if bet > user_coins:
        await interaction.response.send_message(f"❌ 所持金が足りないなえ！ 現在の所持金: {user_coins}ナエン", ephemeral=True)
        return

    coins[user_id] = user_coins - bet
    save_coins()

    view = SlotView(interaction.user, bet)
    embed = Embed(title="スロットマシン", description=f"🎰 ベット: {bet}ナエン。ボタンを押してスロットを回すなえ！", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed, view=view)

# ====== ナエン所持確認 ======

@bot.tree.command(name="naen", description="現在の所持ナエンを確認するなえ！")
async def coin(interaction: Interaction):
    user_id = str(interaction.user.id)
    user_coins = coins.get(user_id, 1000)
    await interaction.response.send_message(f"💰 {interaction.user.mention} さんの現在の所持ナエンは **{user_coins}** ナエンなえ！")

# ====== ブラックジャック (/bj) ======

@bot.tree.command(name="bj", description="ブラックジャックで遊ぶなえ！")
@app_commands.describe(bet="ベットするナエンの数（所持ナエン以内で指定）")
async def blackjack(interaction: discord.Interaction, bet: int):
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    user_id = str(interaction.user.id)

    # 所持ナエン初期化チェック
    if user_id not in coins:
        coins[user_id] = 1000

    # ベット金額チェック
    if bet <= 0:
        await interaction.followup.send("❌ ベットは1以上の数字にしてなえ！")
        return
    if bet > coins[user_id]:
        await interaction.followup.send(f"❌ 所持ナエンが足りなえ！ あなたの所持: {coins[user_id]}ナエン")
        return

    # ベット分を差し引く
    coins[user_id] -= bet
    save_coins()

    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    deck = [rank + suit for rank in ranks for suit in suits]
    random.shuffle(deck)

    def calculate_score(hand):
        score = 0
        ace_count = 0
        for card in hand:
            # "10"は2文字なので判定を工夫
            rank = card[:-1]  # 末尾はスートなので、それ以外をrankとして取得

            if rank in ["J", "Q", "K"]:
                score += 10
            elif rank == "A":
                ace_count += 1
                score += 11
            else:
                score += int(rank)
        # Aを11→1に切り替えてバースト回避
        while score > 21 and ace_count > 0:
            score -= 10
            ace_count -= 1
        return score

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    async def game_embed(hidden=True):
        dealer_display = dealer_hand[0] + " ❓" if hidden else " ".join(dealer_hand)
        dealer_score_text = "" if hidden else f"（合計: {calculate_score(dealer_hand)}）"
        embed = Embed(
            title="🃏 ブラックジャックなえ！",
            description=(
                f"**あなたの手札:** {' '.join(player_hand)}（合計: {calculate_score(player_hand)}）\n"
                f"**なえくんの手札:** {dealer_display} {dealer_score_text}\n"
                f"💰 ベット: {bet}ナエン\n"
                f"🎯 所持ナエン: {coins[user_id]}ナエン"
            ),
            color=discord.Color.dark_green()
        )
        return embed

    class BJView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.user_hand = player_hand
            self.dealer_hand = dealer_hand
            self.deck = deck
            self.bet = bet
            self.user_id = user_id

        @discord.ui.button(label="ヒット！", style=discord.ButtonStyle.primary)
        async def hit(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != int(self.user_id):
                await interaction.response.send_message("⚠️ これはあなたのゲームではなえ！", ephemeral=True)
                return

            self.user_hand.append(self.deck.pop())
            user_score = calculate_score(self.user_hand)
            if user_score > 21:
                # バーストで敗北
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(embed=await game_embed(hidden=False), view=self)
                await interaction.followup.send(
                    f"💥 バーストしたなえ！なえくんの勝ち！ ベットした {self.bet}ナエン は没収なえ！"
                )
                save_coins()
                self.stop()
            else:
                await interaction.response.edit_message(embed=await game_embed(hidden=True), view=self)

        @discord.ui.button(label="スタンド", style=discord.ButtonStyle.secondary)
        async def stand(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != int(self.user_id):
                await interaction.response.send_message("⚠️ これはあなたのゲームではなえ！", ephemeral=True)
                return

            for child in self.children:
                child.disabled = True

            # ディーラーは17以上になるまで引く
            while calculate_score(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())

            user_score = calculate_score(self.user_hand)
            dealer_score = calculate_score(self.dealer_hand)

            if dealer_score > 21 or user_score > dealer_score:
                # プレイヤー勝利
                coins[self.user_id] += self.bet * 2
                result_msg = f"🎉 あなたの勝ちなえ！ ベットした {self.bet}ナエンの2倍をゲット！ 現在の所持: {coins[self.user_id]}ナエン"
            elif user_score < dealer_score:
                # ディーラー勝利
                result_msg = f"😈 なえくんの勝ちなえ〜！ ベットした {self.bet}ナエン は没収なえ… 現在の所持: {coins[self.user_id]}ナエン"
            else:
                # 引き分け
                coins[self.user_id] += self.bet
                result_msg = f"🤝 引き分けなえ！ ベットした {self.bet}ナエン は返却なえ。 現在の所持: {coins[self.user_id]}ナエン"

            save_coins()
            await interaction.response.edit_message(embed=await game_embed(hidden=False), view=self)
            await interaction.followup.send(result_msg)
            self.stop()

    view = BJView()
    await interaction.followup.send(embed=await game_embed(), view=view)

@bot.tree.command(name="give", description="他のユーザーにナエンをプレゼントするなえ！")
@app_commands.describe(
    user="ナエンをあげたいユーザーなえ",
    amount="渡すナエンの数（1ナエン以上）"
)
async def coin_give(interaction: discord.Interaction, user: discord.User, amount: int):
    giver_id = str(interaction.user.id)
    receiver_id = str(user.id)

    # 応答の遅延対策
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    if user.bot:
        await interaction.followup.send("❌ Botにはナエンを送れないなえ！", ephemeral=True)
        return

    if giver_id == receiver_id:
        await interaction.followup.send("❌ 自分にナエンを送ることはできなえ！", ephemeral=True)
        return

    if amount <= 0:
        await interaction.followup.send("❌ 1ナエン以上を指定してなえ！", ephemeral=True)
        return

    # 所持ナエンがないユーザーへの初期化
    if giver_id not in coins:
        coins[giver_id] = 1000
    if receiver_id not in coins:
        coins[receiver_id] = 1000

    if coins[giver_id] < amount:
        await interaction.followup.send(f"❌ 所持ナエンが足りなえ！現在の所持: {coins[giver_id]}ナエン", ephemeral=True)
        return

    # 送金処理
    coins[giver_id] -= amount
    coins[receiver_id] += amount
    save_coins()

    await interaction.followup.send(
        f"🎁 {interaction.user.mention} さんが {user.mention} さんに {amount} ナエンを送ったなえ！\n"
        f"🪙 あなたの残高: {coins[giver_id]} ナエン"
    )

@bot.tree.command(name="avatar", description="指定したユーザーのアイコン画像を表示するなえ！")
@app_commands.describe(user="アイコンを表示したいユーザー（省略すると自分）")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user  # ユーザーが未指定なら自分

    embed = discord.Embed(
        title=f"{user.name} さんのアバター画像",
        color=discord.Color.blue()
    )
    embed.set_image(url=user.display_avatar.url)
    embed.set_footer(text="なえくんBotより")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="naen_ranking", description="所持ナエンのランキングを表示するなえ！")
async def coin_ranking(interaction: discord.Interaction):
    await interaction.response.defer()

    if not coins:
        await interaction.followup.send("誰もナエンを持っていないなえ！")
        return

    ranked = []
    for user_id, coin in coins.items():
        try:
            user = await bot.fetch_user(int(user_id))
            if user.bot:
                continue  # Botはスキップ
            ranked.append((user, coin))
        except Exception:
            continue

    ranked = sorted(ranked, key=lambda x: x[1], reverse=True)[:10]

    if not ranked:
        await interaction.followup.send("ユーザーのナエンデータがありません。")
        return

    lines = [f"{i+1}. {user.name} - {coin}ナエン" for i, (user, coin) in enumerate(ranked)]
    ranking_text = "💰 **ナエン所持ランキング Top 10** 💰\n" + "\n".join(lines)
    await interaction.followup.send(ranking_text)

@bot.tree.command(name="inventory", description="あなたの所持アイテム一覧を表示するなえ！")
async def inventory(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_items = items.get(user_id, {})

    if not user_items:
        await interaction.response.send_message("📦 アイテムはまだ持っていないなえ！")
        return

    item_list = "\n".join([f"{name} × {count}" for name, count in user_items.items()])
    await interaction.response.send_message(f"📦 {interaction.user.mention} さんの所持アイテム:\n{item_list}")

@bot.tree.command(name="gacha", description="1回1000ナエンのガチャを回すなえ！")
async def gacha(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # 応答遅延対応
    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    # 所持ナエン初期化
    if user_id not in coins:
        coins[user_id] = 1000

    # ナエンチェック
    if coins[user_id] < 1000:
        await interaction.followup.send(f"❌ ナエンが足りないなえ！現在の所持: {coins[user_id]}ナエン", ephemeral=True)
        return

    # ナエンを消費
    coins[user_id] -= 1000
    save_coins()

    # レアリティ抽選
    rarity_tiers = [
        {"tier": "normal", "weight": 75, "emoji": ""},
        {"tier": "gold", "weight": 20, "emoji": "🥇"},
        {"tier": "rainbow", "weight": 5, "emoji": "🌈"},
    ]
    tier = random.choices(
        [r["tier"] for r in rarity_tiers],
        weights=[r["weight"] for r in rarity_tiers],
        k=1
    )[0]
    tier_emoji = next(r["emoji"] for r in rarity_tiers if r["tier"] == tier)

    # レアリティごとの報酬テーブル（報酬額も1000ナエンに合わせて調整）
    rewards_by_rarity = {
        "normal": [
            {"type": "naens", "amount": 500, "weight": 45, "message": "💰500ナエンが当たったなえ！"},
            {"type": "item", "name": "はむすたー", "weight": 20, "message": "🐹はむすたーが当たったなえ！"},
            {"type": "item", "name": "らいおん", "weight": 15, "message": "🦁らいおんをゲットしたなえ！"},
            {"type": "item", "name": "さかな", "weight": 10, "message": "🐟さかなが当たったなえ！"},
            {"type": "item", "name": "ねこ", "weight": 5, "message": "🐱ねこをゲットしたなえ！"},
            {"type": "item", "name": "きつね", "weight": 4, "message": "🦊きつねが当たったなえ！"},
            {"type": "item", "name": "ぺんぎん", "weight": 1, "message": "🐧ぺんぎんをゲットしたなえ！"},
        ],
        "gold": [
            {"type": "naens", "amount": 500, "weight": 45, "message": "💰500ナエンが当たったなえ！"},
            {"type": "item", "name": "ゴールドはむすたー", "weight": 20, "message": "🥇🐹はむすたーが当たったなえ！"},
            {"type": "item", "name": "ゴールドらいおん", "weight": 15, "message": "🥇🦁らいおんをゲットしたなえ！"},
            {"type": "item", "name": "ゴールドさかな", "weight": 10, "message": "🥇🐟さかなが当たったなえ！"},
            {"type": "item", "name": "ゴールドねこ", "weight": 5, "message": "🥇🐱ねこをゲットしたなえ！"},
            {"type": "item", "name": "ゴールドきつね", "weight": 4, "message": "🥇🦊きつねが当たったなえ！"},
            {"type": "item", "name": "ゴールドぺんぎん", "weight": 1, "message": "🥇🐧ぺんぎんをゲットしたなえ！"},
        ],
        "rainbow": [
            {"type": "naens", "amount": 500, "weight": 45, "message": "💰500ナエンが当たったなえ！"},
            {"type": "item", "name": "レインボーはむすたー", "weight": 20, "message": "🌈🐹はむすたーが当たったなえ！"},
            {"type": "item", "name": "レインボーらいおん", "weight": 15, "message": "🌈🦁らいおんをゲットしたなえ！"},
            {"type": "item", "name": "レインボーさかな", "weight": 10, "message": "🌈🐟さかなが当たったなえ！"},
            {"type": "item", "name": "レインボーねこ", "weight": 5, "message": "🌈🐱ねこをゲットしたなえ！"},
            {"type": "item", "name": "レインボーきつね", "weight": 4, "message": "🌈🦊きつねが当たったなえ！"},
            {"type": "item", "name": "レインボーぺんぎん", "weight": 1, "message": "🌈🐧ぺんぎんをゲットしたなえ！"},
        ]
    }

    rewards = rewards_by_rarity[tier]
    total_weight = sum(r["weight"] for r in rewards)

    def weighted_choice(choices):
        r = random.uniform(0, total_weight)
        upto = 0
        for c in choices:
            if upto + c["weight"] >= r:
                return c
            upto += c["weight"]
        return choices[-1]

    reward = weighted_choice(rewards)

    # 結果メッセージの組み立て
    msg = f"{interaction.user.mention} さんが {tier_emoji} **{tier.upper()} ガチャ** を引いたなえ！\n"
    msg += f"{reward['message']}\n"

    if reward["type"] == "naens":
        coins[user_id] += reward["amount"]
        save_coins()
        msg += f"🪙 現在の所持ナエン: {coins[user_id]}ナエン"
    elif reward["type"] == "item":
        add_item_to_user(user_id, reward["name"], 1)
        msg += "📦 アイテムは `/inventory` コマンドで確認できるなえ！"

    await interaction.followup.send(msg)

@bot.tree.command(name="gacha10", description="10000ナエンで10連ガチャを回すなえ！")
async def gacha10(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    try:
        await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    if user_id not in coins:
        coins[user_id] = 1000

    if coins[user_id] < 10000:
        await interaction.followup.send(f"❌ ナエンが足りないなえ！現在の所持: {coins[user_id]}ナエン", ephemeral=True)
        return

    # 10000ナエン消費
    coins[user_id] -= 10000
    save_coins()

    # レアリティ抽選設定
    rarity_tiers = [
        {"tier": "normal", "weight": 75, "emoji": ""},
        {"tier": "gold", "weight": 20, "emoji": "🥇"},
        {"tier": "rainbow", "weight": 5, "emoji": "🌈"},
    ]

    # レアリティごとの報酬リスト
    rewards_by_rarity = {
        "normal": [
            {"type": "naens", "amount": 500, "weight": 45, "message": "💰500ナエンが当たったなえ！"},
            {"type": "item", "name": "はむすたー", "weight": 20, "message": "🐹はむすたーが当たったなえ！"},
            {"type": "item", "name": "らいおん", "weight": 15, "message": "🦁らいおんをゲットしたなえ！"},
            {"type": "item", "name": "さかな", "weight": 10, "message": "🐟さかなが当たったなえ！"},
            {"type": "item", "name": "ねこ", "weight": 5, "message": "🐱ねこをゲットしたなえ！"},
            {"type": "item", "name": "きつね", "weight": 4, "message": "🦊きつねが当たったなえ！"},
            {"type": "item", "name": "ぺんぎん", "weight": 1, "message": "🐧ぺんぎんをゲットしたなえ！"},
        ],
        "gold": [
            {"type": "naens", "amount": 500, "weight": 45, "message": "💰500ナエンが当たったなえ！"},
            {"type": "item", "name": "ゴールドはむすたー", "weight": 20, "message": "🐹ゴールドはむすたーが当たったなえ！"},
            {"type": "item", "name": "ゴールドらいおん", "weight": 15, "message": "🦁ゴールドらいおんをゲットしたなえ！"},
            {"type": "item", "name": "ゴールドさかな", "weight": 10, "message": "🐟ゴールドさかなが当たったなえ！"},
            {"type": "item", "name": "ゴールドねこ", "weight": 5, "message": "🐱ゴールドねこをゲットしたなえ！"},
            {"type": "item", "name": "ゴールドきつね", "weight": 4, "message": "🦊ゴールドきつねが当たったなえ！"},
            {"type": "item", "name": "ゴールドぺんぎん", "weight": 1, "message": "🐧ゴールドぺんぎんをゲットしたなえ！"},
        ],
        "rainbow": [
            {"type": "naens", "amount": 500, "weight": 45, "message": "💰500ナエンが当たったなえ！"},
            {"type": "item", "name": "レインボーはむすたー", "weight": 20, "message": "🐹レインボーはむすたーが当たったなえ！"},
            {"type": "item", "name": "レインボーらいおん", "weight": 15, "message": "🦁レインボーらいおんをゲットしたなえ！"},
            {"type": "item", "name": "レインボーさかな", "weight": 10, "message": "🐟レインボーさかなが当たったなえ！"},
            {"type": "item", "name": "レインボーねこ", "weight": 5, "message": "🐱レインボーねこをゲットしたなえ！"},
            {"type": "item", "name": "レインボーきつね", "weight": 4, "message": "🦊レインボーきつねが当たったなえ！"},
            {"type": "item", "name": "レインボーぺんぎん", "weight": 1, "message": "🐧レインボーぺんぎんをゲットしたなえ！"},
        ]
    }

    def weighted_choice(choices):
        total = sum(c["weight"] for c in choices)
        r = random.uniform(0, total)
        upto = 0
        for c in choices:
            if upto + c["weight"] >= r:
                return c
            upto += c["weight"]
        return choices[-1]

    result_messages = [f"{interaction.user.mention} さんが10連ガチャを回したなえ！\n"]

    for i in range(10):
        tier_data = random.choices(
            rarity_tiers,
            weights=[r["weight"] for r in rarity_tiers],
            k=1
        )[0]
        tier = tier_data["tier"]
        tier_emoji = tier_data["emoji"]

        reward = weighted_choice(rewards_by_rarity[tier])
        msg = f"{i+1}回目: {tier_emoji}{reward['message']}"

        if reward["type"] == "naens":
            coins[user_id] += reward["amount"]
        elif reward["type"] == "item":
            add_item_to_user(user_id, reward["name"], 1)

        result_messages.append(msg)

    save_coins()
    result_messages.append(f"🪙 現在の所持ナエン: {coins[user_id]}ナエン")
    result_messages.append("📦 アイテムは `/inventory` で確認できるなえ！")

    await interaction.followup.send("\n".join(result_messages))

from data import all_items, rarity_info  # data.py から読み込み

@bot.tree.command(name="index", description="ゲットしたアイテムの図鑑を表示するなえ！")
async def itemdex(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # 404回避：すでに応答済みでなければ defer
    try:
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)
    except discord.errors.InteractionResponded:
        pass

    # 所持アイテム取得
    user_items = items.get(user_id, {})

    # レアリティ順の表示順設定
    rarity_order = ["rainbow", "gold", "normal"]

    # Embed 初期化
    embed = discord.Embed(title=f"{interaction.user.display_name} さんのアイテム図鑑")

    for rarity_key in rarity_order:
        # 指定レアリティのアイテムだけ抽出
        rarity_items = {k: v for k, v in all_items.items() if v["rarity"] == rarity_key}
        if not rarity_items:
            continue

        # セクション見出し（例：🌈 レインボーアイテム）
        embed.add_field(
            name=f"{rarity_info[rarity_key]['name']}アイテム",
            value="\u200b",
            inline=False
        )

        lines = []
        for name, info in rarity_items.items():
            count = user_items.get(name, 0)
            if count > 0:
                lines.append(f"✅ **{name}** ×{count} — {info['desc']}")
            else:
                lines.append(f"❓ ？？？ — 未入手")

        # 実際の内容を追加
        embed.add_field(
            name="\u200b",
            value="\n".join(lines),
            inline=False
        )

    # 一番高レアな所持アイテムの色を使う
    user_rarities = [
        all_items[name]["rarity"]
        for name, cnt in user_items.items() if cnt > 0 and name in all_items
    ]
    if user_rarities:
        for r in rarity_order:
            if r in user_rarities:
                embed.color = rarity_info[r]["color"]
                break
    else:
        embed.color = discord.Color.dark_gray()

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="help", description="なえくんBotの使い方一覧を表示するなえ！")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📘 なえくんBotの使い方",
        description="以下は、なえくんBotで使えるスラッシュコマンドの一覧なえ！",
        color=discord.Color.blurple()
    )

    embed.add_field(name="🎮 ゲームコマンド", value=(
        "`/janken` - じゃんけんで勝負するなえ！ベットで報酬増加！\n"
        "`/slot` - スロットマシンでナエンを稼ぐなえ！\n"
        "`/bj` - ブラックジャックで勝負なえ！ヒット or スタンドで戦略的に！\n"
        "`/naemikuji` - 1回100ナエンで運試しのおみくじなえ！\n"
        "`/bedwarskit` - なえくんがBedwarsのキットをおすすめするなえ！"
    ), inline=False)

    embed.add_field(name="📈 戦績・ランキング", value=(
        "`/janken_stats` - 自分のじゃんけん戦績を見るなえ！\n"
        "`/janken_ranking` - ランキングで勝者を確認するなえ！"
    ), inline=False)

    embed.add_field(name="💰 ナエン関連", value=(
        "`/naen` - 自分のナエン残高を確認するなえ！\n"
        "`/naen_ranking` - ナエン富豪ランキングを確認するなえ！\n"
        "`/give` - 他のユーザーにナエンを渡すなえ！\n"
    ), inline=False)

    embed.add_field(name="💰 ガチャ関連", value=(
        "`/gacha` - 1回1000ナエンのガチャを回すなえ！\n"
        "`/gacha10` - 10000ナエンで10連ガチャを回すなえ！\n"
        "`/inventory` - あなたの所持アイテム一覧を表示するなえ！\n"
        "`/index` - ゲットしたアイテムの図鑑を表示するなえ！\n"
    ), inline=False)

    embed.add_field(name="🧮 計算", value=(
        "`/sansuu` - 簡単な整数計算ができるなえ！（使うだけで100ナエンもらえる！）"
    ), inline=False)

    embed.add_field(name="🥱 便利", value=(
        "`/avatar` - 指定したユーザーのアイコンを表示するなえ！\n"
    ), inline=False)

    embed.set_footer(text="なえくんBotで遊んでくれてありがとうなえ〜！")

    await interaction.response.send_message(embed=embed)

# --- Bot起動 ---
bot.run(DISCORD_TOKEN)
