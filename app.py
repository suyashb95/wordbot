import json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver


app = APIGatewayRestResolver()


@app.post("/hello")
def hello():
    print(app.current_event.json_body)
    return {"message": "hello unknown!"}


def lambda_handler(event, context):
    return app.resolve(event, context)
