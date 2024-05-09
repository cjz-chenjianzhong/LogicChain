
import requests
import re

g_city_id_dic = {
    '杭州' : '101210101',
}

def get_weather(city_str, interval_str):

    url = 'http://t.weather.sojson.com/api/weather/city/'

    response = requests.get(url + g_city_id_dic[city_str])

    if response.status_code == 200:

        result = response.json()

    else:
        return { 'status' : 'error', 'error_info' : f'http get fail, response code {response.status_code}' }

    # Using Regular Expressions to Match Numbers
    match = re.search(r'\d+', interval_str)

    # If a match is found, then extract the numbers.
    if match:

        day = int(match.group())
        weather_json = result['data']['forecast'][day]

        high_temperature = re.search(r'\d+', weather_json['high']).group()
        low_temperature = re.search(r'\d+', weather_json['low']).group()

        weather_str = f"最高温度{high_temperature}摄氏度, 最低温度{low_temperature}摄氏度, {weather_json['fx']}{weather_json['fl']}, {weather_json['type']};"

        return { 'status' : 'ok', 'result' : weather_str }
    else:

        return { 'status' : 'error', 'error_info' : 'no number in interval string' }