import json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from word_bot import wordbot
import telebot
import json

app = APIGatewayRestResolver()


@app.post("/message")
def hello():
    payload = app.current_event.json_body
    if 'inline_query' not in payload:
        if 'channel_post' in payload:
            return
        if 'edited_message' in payload:
            return
        if 'chosen_inline_result' in payload:
            return
        message = payload.get('message', '')
        if message is None or 'text' not in message or 'reply_to_message' in message:
            return
    try:
        wordbot.process_new_updates([telebot.types.Update.de_json(json.dumps(payload))])
    except:
        pass

def lambda_handler(event, context):
    return app.resolve(event, context)
