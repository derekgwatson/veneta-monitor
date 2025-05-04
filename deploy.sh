#!/bin/bash
clear
set -e

# 🔧 CONFIGURATION
APP_NAME="veneta-monitor"  # Change this for each app

# 🧠 DETECT ENVIRONMENT
CURRENT_DIR=$(dirname "$(realpath "$0")")
if [[ "$CURRENT_DIR" == *"$APP_NAME-staging"* ]]; then
    ENV="staging"
elif [[ "$CURRENT_DIR" == *"$APP_NAME"* ]]; then
    ENV="production"
else
    echo "❌ Could not determine environment from script location: $CURRENT_DIR"
    exit 1
fi

# 🧩 SET SERVICE NAMES
WEB_SERVICE="$APP_NAME.service"
TASK_SERVICE="$APP_NAME-tasks.service"

if [[ "$ENV" == "staging" ]]; then
    WEB_SERVICE="$APP_NAME-staging.service"
    TASK_SERVICE="$APP_NAME-staging-tasks.service"
fi

echo "📁 App: $APP_NAME"
echo "🌐 Environment: $ENV"
echo "🔁 Pulling latest code in $CURRENT_DIR..."
sudo -u www-data git -C "$CURRENT_DIR" pull || { echo "❌ Git pull failed ($ENV)"; exit 1; }

echo "🔄 Restarting systemctl daemon..."
sudo systemctl daemon-reload || { echo "❌ Failed to restart systemctl daemon"; exit 1; }

echo "🔄 Restarting $ENV Flask web app..."
sudo systemctl restart "$WEB_SERVICE" || { echo "❌ Failed to restart web app ($ENV)"; exit 1; }

echo "🔄 Restarting $ENV background tasks..."
sudo systemctl restart "$TASK_SERVICE" || { echo "❌ Failed to restart background tasks ($ENV)"; exit 1; }

echo "🚀 Deploy complete for $APP_NAME ($ENV)."
