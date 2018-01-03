import logging

import json
import requests

from flask import Flask, render_template
from flask_ask import Ask, question, session, statement

TOKEN = 'CYFOVAWPYPSBXVEJFQ6O'

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("EventsInMyAreaIntent", convert={'when': str, })
def answer(when):

    msg = render_template('events')

    return statement(call_eb_api(None))


if __name__ == '__main__':
    app.run(debug=True)


def call_eb_api(when):

    response = requests.post(
        'https://www.eventbriteapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data={
            "event_search": {

                "dates": [
                    "current_future"
                ],
                "page_size": 10,
                "point_radius": {
                    "latitude": -32.895601,
                    "radius": "10km",
                    "longitude": -68.834241
                }
            }
        }
    )
    parsed_response = json.loads(response.text)

    event_descriptions = [
        e.name for e in parsed_response['result']['events']
    ]

    logging.getLogger("flask_ask").debug(event_descriptions)
    return event_descriptions
