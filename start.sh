#!/bin/bash

echo "🔑 Configuring Git authentication..."
git config --global user.email "00nakamidayo@gmail.com"
git config --global user.name "00Nakami"

# Token付きリモートURL設定
git remote set-url origin https://$GITHUB_TOKEN@github.com/00Nakami/discord.bot.git

echo "🔄 Pulling latest data from GitHub..."
git pull origin main

echo "🚀 Starting Discord bot..."
python3 bot.py
