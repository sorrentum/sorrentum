import configparser
import requests

def get_city_weather(lat, lon):
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['API']['weather_key']

    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'imperial' 
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('Error:', response.status_code)
