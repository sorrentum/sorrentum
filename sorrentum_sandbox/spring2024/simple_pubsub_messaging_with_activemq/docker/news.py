import configparser
import requests
from datetime import datetime, timedelta


def get_city_news(city):
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['API']['news_api_key']

    BASE_URL = 'https://newsapi.org/v2/'

    ENDPOINT_TOP_HEADLINES = 'everything'

    current_date_time = datetime.now()
    yesterday_date_time = current_date_time - timedelta(days=1)

    formatted_date = current_date_time.strftime("%Y-%m-%d")
    formatted_date_yest = yesterday_date_time.strftime("%Y-%m-%d")

    params = {
        'q': city, 
        'apiKey': api_key,
        'from':formatted_date_yest,
        'to':formatted_date,
        'sortBy':'popularity',
        'pageSize':50
    }

    response = requests.get(BASE_URL + ENDPOINT_TOP_HEADLINES, params=params)
    data = {}

    if response.status_code == 200:
        data = response.json()
        return data
        
    else:
        print('Error:', response.status_code)

    