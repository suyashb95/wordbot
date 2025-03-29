import datetime
import requests
import telebot
import json

from flask import Flask, request
from config import bot_token
from word_bot import wordbot

app = Flask(__name__)


@app.route("/setWebhook", methods=["GET"])
def root():
    telegram_set_webhook_api = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    webhook = "https://wordbot-455118.lm.r.appspot.com/message"
    payload = {
        "url": webhook,
        "allowed_updates": ["message", "inline_query"]
    }
    response = requests.post(
        telegram_set_webhook_api,
        data = payload
    )
    if response.ok:
        return "Webhook set successfully"
    return f"Error while setting webhook {response.text}"

@app.route("/message", methods=["POST"])
def process_update():
    request_data = request.get_json()
    if request_data['message']['text']:
        wordbot.process_new_updates([telebot.types.Update.de_json(json.dumps(request_data))])
    return {
        "statusCode": 200
    }

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)