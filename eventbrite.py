import logging

import json
import requests

import urllib
from flask import Flask, render_template
from flask_ask import Ask, request, question, session, statement, context

from eb_api_connector import call_eb_api_for_next_event

TOKEN = '7FLR77ARPTR4VLY3JFMU'

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("EventsInMyAreaIntent", convert={'when': str, "city": str })
def answer(when, city):
    event = call_eb_api(when, city)
    return statement(event)


def get_place_id(city):
    city = urllib.urlencode({'q': city})
    url = "https://www.evbqaapi.com/v3/destination/search/places/?token={TOKEN}&q={city}"
    response = requests.get(url)
    parsed_response = json.loads(response.text)

    if parsed_response.get('places'):
        places = [
            place['id']
            for place in parsed_response['places']
            if place['place_type'] == 'locality'
        ]
        return places[:1]


def call_eb_api(when):
    date_range = {"to": when, "from": when}
    response = requests.post(
        'https://www.evbqaapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data=json.dumps({
            "event_search": {
                "date_range": date_range,
                "page_size": 1,

            }
        }),
        headers={'content-type': 'application/json'},
    )
    parsed_response = json.loads(response.text)
    response = ""
    if parsed_response['events']['results']:
        e = parsed_response['events']['results'][0]

        event = {'title': e['name'], 'content': e['summary']}
        response = 'This event is happening in your area: {}'.format(event['title']).simple_card(**event)
    else:
        response = "There is no live events to attend."
    return response


def get_alexa_location():
    URL = "https://api.amazonalexa.com/v1/devices/{}/settings" \
        "/address".format(context.System.device.deviceId)
    TOKEN = context.System.user.permissions.consentToken
    HEADER = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(TOKEN)}
    r = requests.get(URL, headers=HEADER)
    if r.status_code == 200:
        return(r.json())


@ask.intent("NextEventInMyAreaIntent", convert={"city": str})
def next_event_in_city(city):
    events_to_alexa, alexa_message = call_eb_api_for_next_event(city)
    return statement(alexa_message) \
        .standard_card(
            title=events_to_alexa[0]['name'],
            text=events_to_alexa[0]['summary'],
            large_image_url=events_to_alexa[0]['image'],
        )


if __name__ == '__main__':
    app.run(debug=True)
