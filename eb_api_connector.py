import json

import requests

from collections import OrderedDict

TOKEN = '7FLR77ARPTR4VLY3JFMU'


def call_eb_api_for_next_event(city):
    response = requests.post(
        'https://www.evbqaapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data=json.dumps({
            "event_search": {
                "dates": [
                    "current_future"
                ],
                "page_size": 20,
                "point_radius": {
                    "latitude": 37.781973,
                    "radius": "10km",
                    "longitude": -122.405385
                }
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
        for values in candidate_events_to_alexa.values()[:3]
    ]
    message = 'Hi! There is three events in your region: {}'.format(
            '. '.join(itens_to_message)
        )
    import ipdb; ipdb.set_trace()
    return (candidate_events_to_alexa.values()[:3], message)
