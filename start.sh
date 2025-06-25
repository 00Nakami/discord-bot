#!/bin/bash

echo "🔑 Configuring Git authentication..."
git config --global user.email "00nakamidayo@gmail.com"
git config --global user.name "00Nakami"

# GitHub リモートに Token を含んだ URL をセット
git remote set-url origin https://$GITHUB_TOKEN@github.com/00Nakami/discord-bot.git

echo "🔄 Pulling latest coins.json from GitHub..."
git pull origin main

echo "🚀 Starting Discord bot..."
python3 bot.py
