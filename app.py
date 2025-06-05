import os
import requests
from dotenv import load_dotenv

def get_weather(city_name, api_key):
    """
    ฟังก์ชันสำหรับดึงข้อมูลสภาพอากาศจาก OpenWeatherMap API
    
    Args:
        city_name (str): ชื่อเมืองที่ต้องการตรวจสอบสภาพอากาศ
        api_key (str): API Key สำหรับใช้งาน OpenWeatherMap
        
    Returns:
        dict: ข้อมูลสภาพอากาศในรูปแบบ dictionary
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',  # ใช้หน่วยเมตริก (องศาเซลเซียส)
        'lang': 'th'  # ใช้ภาษาไทย
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # ตรวจสอบข้อผิดพลาด HTTP
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 401:
            print("\n⚠️ ข้อผิดพลาด: API Key ไม่ถูกต้องหรือหมดอายุ")
            print("กรุณาตรวจสอบ API Key ในไฟล์ .env ให้ถูกต้อง")
            print("วิธีรับ API Key ฟรี: https://home.openweathermap.org/api_keys\n")
        else:
            print(f"\n⚠️ เกิดข้อผิดพลาด HTTP {http_err.response.status_code}: {http_err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return None

def display_weather(weather_data):
    """
    แสดงข้อมูลสภาพอากาศในรูปแบบที่อ่านง่าย
    
    Args:
        weather_data (dict): ข้อมูลสภาพอากาศที่ได้จาก API
    """
    if not weather_data or 'main' not in weather_data:
        print("ไม่สามารถดึงข้อมูลสภาพอากาศได้")
        return
    
    try:
        city = weather_data['name']
        country = weather_data['sys']['country']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        weather_desc = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']
        
        print("\n" + "="*50)
        print(f"สภาพอากาศที่ {city}, {country}")
        print("="*50)
        print(f"อุณหภูมิ: {temp}°C (รู้สึกเหมือน {feels_like}°C)")
        print(f"สภาพอากาศ: {weather_desc}")
        print(f"ความชื้น: {humidity}%")
        print(f"ความเร็วลม: {wind_speed} m/s")
        print("="*50 + "\n")
        
    except KeyError as e:
        print(f"เกิดข้อผิดพลาดในการแสดงข้อมูล: ไม่พบข้อมูล {e}")

def main():
    # โหลด API Key จากไฟล์ .env
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key:
        print("ไม่พบ API Key กรุณาตั้งค่า OPENWEATHER_API_KEY ในไฟล์ .env")
        return
    
    print("=== Weather App ===")
    print("พิมพ์ 'ออก' เพื่อปิดโปรแกรม")
    
    while True:
        city = input("\nกรุณาใส่ชื่อเมืองที่ต้องการตรวจสอบสภาพอากาศ: ")
        
        if city.lower() == 'ออก':
            print("ขอบคุณที่ใช้บริการ")
            break
            
        if city.strip() == "":
            print("กรุณาใส่ชื่อเมือง")
            continue
            
        weather_data = get_weather(city, api_key)
        
        if weather_data and 'cod' in weather_data and weather_data['cod'] == 200:
            display_weather(weather_data)
        else:
            error_msg = weather_data.get('message', 'ไม่ทราบข้อผิดพลาด') if weather_data else 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้'
            print(f"ไม่พบข้อมูลสำหรับเมือง {city}: {error_msg}")

if __name__ == "__main__":
    main()
