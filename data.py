import discord

# アイテムリスト（アイテム名 → 説明とレアリティ）
all_items = {
    "はむすたー": {"desc": "🐹 小さくてかわいい！", "rarity": "normal"},
    "らいおん": {"desc": "🦁 ジャングルの王者！", "rarity": "normal"},
    "さかな": {"desc": "🐟 おいしそうなさかな！", "rarity": "normal"},
    "ねこ": {"desc": "🐱 にゃん！", "rarity": "normal"},
    "きつね": {"desc": "🦊 狡猾なきつね！", "rarity": "normal"},
    "ぺんぎん": {"desc": "🐧 氷の上を歩くなえ！", "rarity": "normal"},
    "ゴールドはむすたー": {"desc": "🐹 小さくてかわいい！", "rarity": "gold"},
    "ゴールドらいおん": {"desc": "🦁 ジャングルの王者！", "rarity": "gold"},
    "ゴールドさかな": {"desc": "🐟 おいしそうなさかな！", "rarity": "gold"},
    "ゴールドねこ": {"desc": "🐱 にゃん！", "rarity": "gold"},
    "ゴールドきつね": {"desc": "🦊 狡猾なきつね！", "rarity": "gold"},
    "ゴールドぺんぎん": {"desc": "🐧 氷の上を歩くなえ！", "rarity": "gold"},
    "レインボーはむすたー": {"desc": "🐹 小さくてかわいい！", "rarity": "rainbow"},
    "レインボーらいおん": {"desc": "🦁 ジャングルの王者！", "rarity": "rainbow"},
    "レインボーさかな": {"desc": "🐟 おいしそうなさかな！", "rarity": "rainbow"},
    "レインボーねこ": {"desc": "🐱 にゃん！", "rarity": "rainbow"},
    "レインボーきつね": {"desc": "🦊 狡猾なきつね！", "rarity": "rainbow"},
    "レインボーぺんぎん": {"desc": "🐧 氷の上を歩くなえ！", "rarity": "rainbow"},
}

# レアリティごとの情報（表示名とEmbedカラー）
rarity_info = {
    "normal": {"name": "ノーマル", "color": discord.Color.light_gray()},
    "gold": {"name": "ゴールド", "color": discord.Color.gold()},
    "rainbow": {"name": "レインボー", "color": discord.Color.magenta()},
}
