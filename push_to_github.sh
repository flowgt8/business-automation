#!/bin/bash
# GitHub setup script
# Run this to push to your GitHub account

GITHUB_USER="flowgt8"
REPO_NAME="business-automation"

# Add remote
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Push to GitHub
git push -u origin master

echo "✅ Pushed to https://github.com/$GITHUB_USER/$REPO_NAME"
