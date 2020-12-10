from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from datetime import datetime
import requests
from pytz import timezone


index = never_cache(TemplateView.as_view(template_name='index.html'))


def stations(request):
    stations = get_stations()
    return JsonResponse(stations, safe=False)


def schedules(request):
    station = request.GET.get('station')
    schedules = get_schedules(station)

    return JsonResponse(schedules, safe=False)


def get_stations():
    stops_url = "https://api-v3.mbta.com/stops?page[offset]=0&page[limit]=300&sort=name&fields[stop]='id'&include=route&filter[route_type]=2"
    data = do_get(stops_url)
    station_names = [s.get('id') for s in data.get('data')]

    return station_names


def get_schedules(station):
    departures = []
    outbound = []
    inbound = []
    tz = timezone('EST')
    filter_date = datetime.now(tz).date()
    min_time = get_time_12hr(datetime.now(tz))
    r = do_get(f'https://api-v3.mbta.com/schedules?sort=departure_time&fields[schedule]=departure_time,direction_id&include=stop,trip,prediction,route&filter[date]={filter_date}&filter[min_time]={min_time}&filter[stop]={station}')

    data = r.get('data')
    for s in data:
        direction = s['attributes']['direction_id']
        if s.get('attributes').get('departure_time'):
            timestamp = s['attributes']['departure_time']

            rels = s['relationships']
            trip_id = rels['trip']['data']['id']
            stop_id = rels['stop']['data']['id']
            if rels['prediction']['data']:
                prediction_id = rels['prediction']['data']['id']
            else:
                prediction_id = None
            trip_data = get_trip_status_data(r.get('included'), trip_id, stop_id, prediction_id)

            row = {
                'time': get_time(timestamp),
                'destination': trip_data.get('destination'),
                'train': trip_data.get('name'),
                'track': trip_data.get('track'),
                'status': 'Scheduled' if direction == 0 else trip_data.get('status'),
                'direction': 'Outbound' if direction == 0 else 'Inbound'
            }

            if direction == 0:
                outbound.append(row)
            else:
                inbound.append(row)

    return {'station': station, 'inbound': inbound, 'outbound': outbound}


def get_date(date):
    return date.strftime("%Y-%m-%d")


def get_time(date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
    return date.strftime("%I:%M:%S%p")


def get_time_12hr(date):
    return date.strftime("%H:%M")


def get_trip_status_data(included, trip_id, stop_id, prediction_id=None):
    trip_data = {'status': 'On time'}

    for include in included:
        include_id = include.get('id')
        if include_id == trip_id:
            trip_data.update({
                "destination": include["attributes"]["headsign"],
                "name": include["attributes"]["name"]
            })
        elif include_id == stop_id:
            track = include["attributes"]["platform_code"]
            trip_data.update({
                "track": track if track else 'TBA'
            })
        elif prediction_id and include_id == prediction_id:
            if include["attributes"]["status"]:
                trip_data.update({
                    "status": include["attributes"]["status"]
                })
    return trip_data


def do_get(url):
    r = requests.get(url)

    if r.status_code != 200:
        return None

    return r.json()

