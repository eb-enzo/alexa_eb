import logging

import json
import requests

from flask import Flask, render_template
from flask_ask import Ask, question, session, statement

TOKEN = '7FLR77ARPTR4VLY3JFMU'

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("EventsInMyAreaIntent", convert={'when': str, })
def answer(when):
    event = call_eb_api(None)
    result = statement('This event is happening in your area').simple_card(**event)

    return result


def call_eb_api(when):

    response = requests.post(
        'https://www.evbqaapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data=json.dumps({
            "event_search": {
                "dates": [
                    "current_future"
                ],
                "page_size": 1,
                "page_number": 1,
                "point_radius": {
                    "latitude": -32.895601,
                    "radius": "10km",
                    "longitude": -68.834241
                }
            }
        }),
        headers={'content-type': 'application/json'},
    )
    parsed_response = json.loads(response.text)
    e = parsed_response['events']['results'][0]

    event_description = {'title': e['name'], 'content': e['summary']}

    return event_description


if __name__ == '__main__':
    app.run(debug=True)
