import json

import requests

TOKEN = '7FLR77ARPTR4VLY3JFMU'

def call_eb_api_for_next_event(city):
    response = requests.post(
        'https://www.evbqaapi.com/v3/destination/search/?token={}'.format(TOKEN),
        data=json.dumps({
            "event_search": {
                "dates": [
                    "current_future"
                ],
                "page_size": 1,
                "point_radius": {
                    "latitude": 37.781973,
                    "radius": "10km",
                    "longitude": -122.405385
                }
            }
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