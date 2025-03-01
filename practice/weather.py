import requests

# OpenWeatherMap API 키 (자신의 API 키로 변경)
API_KEY = "YOUR_API_KEY"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"


def get_weather(city, unit="metric"):
    """도시의 현재 날씨 정보를 가져오는 함수"""
    units_label = "°C" if unit == "metric" else "°F"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": unit,  # 섭씨(metric) 또는 화씨(imperial) 단위 선택
        "lang": "kr",
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()

        city_name = weather_data["name"]
        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        weather_description = weather_data["weather"][0]["description"]

        weather_info = (
            f"\n📍 도시: {city_name}\n"
            f"🌡️ 온도: {temperature}{units_label} (체감: {feels_like}{units_label})\n"
            f"💧 습도: {humidity}%\n"
            f"💨 풍속: {wind_speed} Km/h\n"
            f"☁️ 날씨 상태: {weather_description}\n"
        )

        print(weather_info)

        # 로그 파일 저장
        with open("weather_log.txt", "a", encoding="utf-8") as file:
            file.write(weather_info + "=" * 40 + "\n")

        print("💾 날씨 정보가 'weather_log.txt' 파일에 저장되었습니다!")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 날씨 정보를 가져올 수 없습니다: {e}")


def get_forecast(city, unit="metric"):
    """도시의 5일간 날씨 예보를 가져오는 함수"""
    units_label = "°C" if unit == "metric" else "°F"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": unit,
        "lang": "kr",
        "cnt": 5,  # 5일 예보
    }

    try:
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        forecast_data = response.json()

        print(f"\n📅 {city}의 5일간 날씨 예보:")
        for forecast in forecast_data["list"][:5]:  # 처음 5개의 데이터만 출력
            temp = forecast["main"]["temp"]
            weather_desc = forecast["weather"][0]["description"]
            print(f"📌 온도: {temp}{units_label} - {weather_desc}")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 날씨 예보를 가져올 수 없습니다: {e}")


def weather_app():
    """날씨 조회 프로그램 실행"""
    while True:
        print("\n🌤️ 날씨 정보 프로그램")
        print("1. 현재 날씨 조회")
        print("2. 5일간의 날씨 예보")
        print("3. 종료")

        choice = input("👉 원하는 기능을 선택하세요: ")

        if choice in ["1", "2"]:
            city = input("🌍 날씨를 조회할 도시명을 입력하세요: ").strip()
            unit = (
                input("🌡️ 단위를 선택하세요 (섭씨: C / 화씨: F) [기본: C]: ")
                .strip()
                .lower()
            )
            unit = "metric" if unit == "c" or unit == "" else "imperial"

            if choice == "1":
                get_weather(city, unit)
            elif choice == "2":
                get_forecast(city, unit)
        elif choice == "3":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")


# 실행
weather_app()
