import logging

import json
import requests

from flask import Flask, render_template
from flask_ask import Ask, question, session, statement, context

from eb_api_connector import (
    call_eb_api_for_next_event,
    get_place_ids,
)


TOKEN = '7FLR77ARPTR4VLY3JFMU'

app = Flask(__name__)

ask = Ask(app, "/")

logger = logging.getLogger()


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("EventsInMyAreaIntent", convert={'when': str, "city": str})
def answer(when, city):
    logger.info("parameters when: {} ,city: {}".format(when, city))

    place_ids = get_place_ids(city)
    event = call_eb_api(when, place_ids)
    return statement(event)


@ask.intent("EventsInMyAreaByCategoryIntent", convert={'when': str, "city": str, "category": str})
def answer_by_category(when, city, category):
    logger.info("parameters when: {} ,city: {}, category: {}".format(when, city, category))

    place_ids = get_place_ids(city)
    event = call_eb_api_with_category(when, place_ids, category)
    return statement(event)


def call_eb_api(when, place_ids):
    response = requests.post(
        'https://www.evbqaapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data=json.dumps({
            "event_search": {
                "date_range": {"to": when, "from": when},
                "page_size": 1,
                "places": place_ids,
            },
        }),
        headers={'content-type': 'application/json'},
    )

    parsed_response = response.json()
    response = ""

    if parsed_response['events']['results']:
        e = parsed_response['events']['results'][0]

        event = {'title': e['name'], 'content': e['summary']}
        response = 'This event is happening in your area: {}'.format(event['title'])
    else:
        response = "There are no live events to attend."
    return response


def call_eb_api_with_category(when, place_ids, category):
    category_id_map = {
        "music": "103",
        "sports": "108",
        "fitness": "108",
        "food": "110",
        "drink": "110",
        "drinking": "110",
        "charity": "111",
        "science": "102",
        "technology": "102",
        "tech": "102",
        "business": "101",
        "professional": "101",
    }

    response = requests.get(
        'https://www.evbqaapi.com/v3/destination/search/events/',
        params={
                "token": TOKEN,
                "place": place_ids[0],
                "categories": category_id_map.get(category, ""),
                "start_date.range_start": when+"T00:00:00Z",
                "start_date.range_end": when+"T23:59:59Z",
                "expand.destination_event": "image"
        },
        headers={'content-type': 'application/json'},
    )

    parsed_response = response.json()
    response = ""

    if parsed_response['events']:
        e = parsed_response['events'][0]

        event = {'title': e['name'], 'content': e['summary']}
        response = 'This event is happening in your area: {}'.format(event['title'])
    else:
        response = "There are no live events to attend."
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
    place_ids = get_place_ids(city)

    events_to_alexa, alexa_message = call_eb_api_for_next_event(place_ids)
    return statement(alexa_message) \
        .standard_card(
            title=events_to_alexa[0]['name'],
            text=events_to_alexa[0]['summary'],
            large_image_url=events_to_alexa[0]['image'],
        )


if __name__ == '__main__':
    # place_ids = get_place_ids("New York")
    # events_to_alexa, alexa_message = call_eb_api_for_next_event(place_ids)
    # print events_to_alexa
    app.run(debug=True)
