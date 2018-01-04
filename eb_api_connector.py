import logging
import json

import requests

TOKEN = '7FLR77ARPTR4VLY3JFMU'

logger = logging.getLogger()


def call_eb_api_for_next_event(place_ids):
    response = requests.post(
        'https://www.evbqaapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data=json.dumps({
            "event_search": {
                "dates": [
                    "current_future"
                ],
                "page_size": 1,
                "places": place_ids,
            },
            "expand.destination_event": [
                "primary_venue",
                "image"
            ],
            "expand.destination_profile": [
                "image"
            ],
            "expand.article": [
                "image"
            ]
        }),
        headers={'content-type': 'application/json'},
    )
    parsed_response = json.loads(response.text)
    response = ""
    if parsed_response['events']['results']:
        # e = parsed_response['events']['results'][0]

        # event = {'title': e['name'], 'content': e['summary']}
        # events = [
        #     event['name']
        #     for event in parsed_response['events']['results']
        # ]
        return parsed_response['events']['results']
        # response = 'This event is happening in your area: {}'.format(e['name'])

    return []


def get_place_ids(city):

    url = "https://www.evbqaapi.com/v3/destination/search/places/?token={token}&q={city}".format(
        city=city,
        token=TOKEN,
    )

    logger.info("looking for places url: {}".format(url))
    response = requests.get(url)
    places = response.json().get('places', [])

    places = [
        place['id']
        for place in places
        if place['place_type'] == 'locality'
    ]
    logger.info("places: {}".format(places))
    return places[:1]
