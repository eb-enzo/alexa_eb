import logging
import json

import requests

from collections import OrderedDict

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

    results_from_eb = response.json()
    candidate_events_to_alexa = OrderedDict()
    for res in results_from_eb['events']['results']:
        candidate_events_to_alexa[res['eid']] = {
            'name': res['name'].encode('utf-8'),
            'summary': res['summary'].encode('utf-8'),
            'iamges': res['image']['original']['url'],
            'start_date': res['start_date'],
            'start_time': res['start_time'],
        }

    itens_to_message = [
        '{} in {} starting at {}'.format(
            res['name'].encode('utf-8'),
            res['start_date'],
            res['start_time'],
        )
        for res in candidate_events_to_alexa.values()[:3]
    ]
    message = 'Hi! There is three events in your region: {}'.format(
            '. '.join(itens_to_message)
        )
    return (candidate_events_to_alexa.values()[:3], message)


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
