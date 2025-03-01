#!/bin/bash

# Replace with your bot's API token
BOT_TOKEN="your-bot-token"
# Replace with your webhook URL
WEBHOOK_URL="example-webhook"

# The API URL for setWebhook
API_URL="https://api.telegram.org/bot$BOT_TOKEN/setWebhook"
# Make the API call using curl
response=$(curl -s -X POST $API_URL -d "url=$WEBHOOK_URL")

# Check if the response contains the expected success message
if [[ "$response" == *"\"ok\":true"* ]]; then
  echo "Webhook set successfully!"
else
  echo "Failed to set webhook. Response: $response"
fi
