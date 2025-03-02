#!/bin/bash

# Replace with your bot's API token
BOT_TOKEN="your-bot-token"
# Replace with your webhook URL
WEBHOOK_URL="example-webhook"

# The API URL for setWebhook
API_URL="https://api.telegram.org/bot$BOT_TOKEN/setWebhook"

# Prepare the JSON payload using single quotes
json_data='{
  "url": "'"$WEBHOOK_URL"'",
  "allowed_updates": ["message", "inline_query"]
}'

# Make the API call using curl with JSON body
response=$(curl -s -X POST $API_URL -H "Content-Type: application/json" -d "$json_data")

# Check if the response contains the expected success message
if [[ "$response" == *"\"ok\":true"* ]]; then
  echo "Webhook set successfully!"
else
  echo "Failed to set webhook. Response: $response"
fi
