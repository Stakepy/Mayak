import requests
from config import OPENWEATHERMAP_API_KEY


async def get_weather(city: str, country: str) -> str:
    # URL для запроса погоды через OpenWeatherMap с параметром на русском языке
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={OPENWEATHERMAP_API_KEY}&lang=ru&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Получение основных данных
        city_name = data['name']
        country_name = data['sys']['country']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        description = data['weather'][0]['description']

        # Формирование текста прогноза
        forecast = (f"**{city_name}, {country_name}**:\n"
                    f"Температура: {temp}°C\n"
                    f"Влажность: {humidity}%\n"
                    f"Скорость ветра: {wind_speed} м/с\n"
                    f"Описание: {description.capitalize()}")

        return forecast
    else:
        return "❌ Ошибка получения данных о погоде."
