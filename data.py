import discord
import json
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return default

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

coins = load_json("coins.json", {})
items = load_json("items.json", {})
stats = load_json("stats.json", {})
equipped = load_json("equipped.json", {})  # ⭐ 装備データの追加

def save_coins(): save_json("coins.json", coins)
def save_items(): save_json("items.json", items)
def save_stats(): save_json("stats.json", stats)
def save_equipped(): save_json("equipped.json", equipped)

def load_all_data():
    global coins, items, stats, equipped
    coins = load_json("coins.json", {})
    items = load_json("items.json", {})
    stats = load_json("stats.json", {})
    equipped = load_json("equipped.json", {})

# アイテムリスト（アイテム名 → 説明とレアリティ）
all_items = {
    "はむすたー": {"desc": "🐹 小さくてかわいい！", "rarity": "normal", "power": 1},
    "らいおん": {"desc": "🦁 ジャングルの王者！", "rarity": "normal", "power": 2},
    "さかな": {"desc": "🐟 おいしそうなさかな！", "rarity": "normal", "power": 3},
    "ねこ": {"desc": "🐱 にゃん！", "rarity": "normal", "power": 4},
    "きつね": {"desc": "🦊 狡猾なきつね！", "rarity": "normal", "power": 5},
    "ぺんぎん": {"desc": "🐧 氷の上を歩くなえ！", "rarity": "normal", "power": 6},
    "ゴールドはむすたー": {"desc": "🐹 小さくてかわいい！", "rarity": "gold", "power": 2},
    "ゴールドらいおん": {"desc": "🦁 ジャングルの王者！", "rarity": "gold", "power": 4},
    "ゴールドさかな": {"desc": "🐟 おいしそうなさかな！", "rarity": "gold", "power": 6},
    "ゴールドねこ": {"desc": "🐱 にゃん！", "rarity": "gold", "power": 8},
    "ゴールドきつね": {"desc": "🦊 狡猾なきつね！", "rarity": "gold", "power": 10},
    "ゴールドぺんぎん": {"desc": "🐧 氷の上を歩くなえ！", "rarity": "gold", "power": 12},
    "レインボーはむすたー": {"desc": "🐹 小さくてかわいい！", "rarity": "rainbow", "power": 4},
    "レインボーらいおん": {"desc": "🦁 ジャングルの王者！", "rarity": "rainbow", "power": 8},
    "レインボーさかな": {"desc": "🐟 おいしそうなさかな！", "rarity": "rainbow", "power": 12},
    "レインボーねこ": {"desc": "🐱 にゃん！", "rarity": "rainbow", "power": 16},
    "レインボーきつね": {"desc": "🦊 狡猾なきつね！", "rarity": "rainbow", "power": 20},
    "レインボーぺんぎん": {"desc": "🐧 氷の上を歩くなえ！", "rarity": "rainbow", "power": 24},
}

# レアリティごとの情報（表示名とEmbedカラー）
rarity_info = {
    "normal": {"name": "ノーマル", "color": discord.Color.light_gray()},
    "gold": {"name": "ゴールド", "color": discord.Color.gold()},
    "rainbow": {"name": "レインボー", "color": discord.Color.magenta()},
}
