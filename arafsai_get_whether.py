import os
import requests
import logging
from dotenv import load_dotenv
from livekit.agents import function_tool  

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_city_by_ip() -> str:
    try:
        logger.info("IP এর মাধ্যমে শহর শনাক্ত করার চেষ্টা করা হচ্ছে...")
        ip_info = requests.get("https://ipapi.co/json/").json()
        city = ip_info.get("city")
        return city if city else "Dhaka"
    except Exception as e:
        logger.error(f"সিটি শনাক্তকরণে এরর: {e}")
        return "Dhaka"

@function_tool
async def get_weather(city: str = "") -> str:
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        logger.error("OpenWeather API key পাওয়া যায়নি।")
        return "Environment variables-এ OpenWeather API key নেই।"

    if not city:
        city = detect_city_by_ip()

    logger.info(f"শহর: {city} এর আবহাওয়া খোঁজা হচ্ছে...")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return f"এরর: {city} এর আবহাওয়া পাওয়া যায়নি। সঠিক নাম যাচাই করুন।"

        data = response.json()
        weather = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        # রেজাল্ট ফরম্যাট ঠিক করা হয়েছে
        result = (f"Weather in {city}:\n"
                  f"- Condition: {weather}\n"
                  f"- Temperature: {temp}°C\n"
                  f"- Humidity: {humidity}%\n"
                  f"- Wind Speed: {wind} m/s")

        logger.info(f"Weather result: \n{result}")
        return result

    except Exception as e:
        logger.exception(f"আবহাওয়া ডেটা প্রসেসিং এরর: {e}")
        return "আবহাওয়া ডেটা পাওয়ার সময় এরর হয়েছে।"