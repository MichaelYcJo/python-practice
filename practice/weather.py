import requests

# OpenWeatherMap API 키 (자신의 API 키로 변경)
API_KEY = "YOUR_API_KEY"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    """도시의 현재 날씨 정보를 가져오는 함수"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # 섭씨(Celsius) 단위
        "lang": "kr",  # 한글 출력
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()

        city_name = weather_data["name"]
        temperature = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        weather_description = weather_data["weather"][0]["description"]

        print(f"\n📍 도시: {city_name}")
        print(f"🌡️ 온도: {temperature}°C")
        print(f"💧 습도: {humidity}%")
        print(f"☁️ 날씨 상태: {weather_description}")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 날씨 정보를 가져올 수 없습니다: {e}")


# 사용 예시
city = input("🌍 날씨를 조회할 도시명을 입력하세요: ")
get_weather(city)
