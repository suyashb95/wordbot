import json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from word_bot import wordbot
import telebot
import json

app = APIGatewayRestResolver()


@app.post("/message")
def hello():
    payload = app.current_event.json_body
    if 'message' in payload and 'reply_to_message' in payload.get('message'): return
    wordbot.process_new_updates([telebot.types.Update.de_json(json.dumps(payload))])

def lambda_handler(event, context):
    return app.resolve(event, context)
