import requests


class Searching:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def return_weather(self):
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}'
            f'&appid=da89af6811e205f769fe66a24ef71226&units=metric&lang=en')
        print(str(response.json()['weather'][0]['main']))
        print(str(response.json()['weather'][0]['description']))
        if str(response.json()['weather'][0]['main']) == "Clouds":
            if str(response.json()['weather'][0][
                       'description']) == "few clouds":
                return ' '.join(
                    [str(int(response.json()['main']['temp'])),
                     'Few_clouds'])
            if str(response.json()['weather'][0][
                       'description']) == "scattered clouds":
                return ' '.join(
                    [str(int(response.json()['main']['temp'])),
                     'Scattered_clouds'])
            if str(response.json()['weather'][0][
                       'description']) == "broken clouds":
                return ' '.join(
                    [str(int(response.json()['main']['temp'])),
                     'Broken_clouds'])
            if str(response.json()['weather'][0][
                       'description']) == "overcast clouds":
                return ' '.join(
                    [str(int(response.json()['main']['temp'])),
                     'Broken_clouds'])

        return ' '.join([str(int(response.json()['main']['temp'])),
                         str(response.json()['weather'][0]['main'])])
