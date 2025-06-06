from flask import Flask, render_template, request, jsonify
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS สำหรับทุก route

# โหลด API Key จากไฟล์ .env
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather(city_name, api_key):
    """
    ฟังก์ชันสำหรับดึงข้อมูลสภาพอากาศจาก OpenWeatherMap API
    
    Args:
        city_name (str): ชื่อเมืองที่ต้องการตรวจสอบสภาพอากาศ
        api_key (str): API Key สำหรับใช้งาน OpenWeatherMap
        
    Returns:
        dict: ข้อมูลสภาพอากาศในรูปแบบ dictionary
    """
    if not api_key or api_key == 'your_api_key_here':
        print("Error: ยังไม่ได้ตั้งค่า API Key ในไฟล์ .env")
        return {'error': 'กรุณาตั้งค่า OpenWeatherMap API Key ในไฟล์ .env'}
    
    print(f"\n=== กำลังดึงข้อมูลสภาพอากาศ ===")
    print(f"เมือง: {city_name}")
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',  # ใช้หน่วยเมตริก (องศาเซลเซียส)
        'lang': 'th'  # ใช้ภาษาไทย
    }
    
    print(f"URL: {base_url}")
    print(f"Parameters: {params}")
    
    try:
        # ส่งคำขอไปยัง OpenWeatherMap API
        print("\n=== ส่งคำขอไปยัง OpenWeatherMap ===")
        response = requests.get(base_url, params=params)
        
        # ตรวจสอบสถานะการตอบกลับ
        print("\n=== การตอบกลับจาก API ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
        # พยายามแปลงข้อมูล JSON
        data = response.json()
        print(f"Response JSON: {data}")
        
        # ตรวจสอบสถานะการตอบกลับ
        if response.status_code != 200:
            error_msg = data.get('message', 'เกิดข้อผิดพลาดในการเชื่อมต่อกับ OpenWeatherMap API')
            print(f"Error: {error_msg}")
            return {'error': error_msg}
            
        print("\n=== ดึงข้อมูลสำเร็จ ===")
        return data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}"
        print(f"Error: {error_msg}")
        return {'error': error_msg}
    except json.JSONDecodeError as e:
        error_msg = f"เกิดข้อผิดพลาดในการแปลงข้อมูล JSON: {str(e)}"
        print(f"Error: {error_msg}")
        return {'error': 'เกิดข้อผิดพลาดในการประมวลผลข้อมูลจาก API'}
    except Exception as e:
        error_msg = f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {str(e)}"
        print(f"Error: {error_msg}")
        return {'error': 'เกิดข้อผิดพลาดในการดึงข้อมูลสภาพอากาศ'}

def get_forecast(city_name, api_key):
    """
    ฟังก์ชันสำหรับดึงข้อมูลพยากรณ์อากาศ 5 วัน จาก OpenWeatherMap API
    
    Args:
        city_name (str): ชื่อเมืองที่ต้องการตรวจสอบพยากรณ์อากาศ
        api_key (str): API Key สำหรับใช้งาน OpenWeatherMap
        
    Returns:
        dict: ข้อมูลพยากรณ์อากาศในรูปแบบ dictionary
    """
    if not api_key or api_key == 'your_api_key_here':
        return {'error': 'กรุณาตั้งค่า OpenWeatherMap API Key ในไฟล์ .env'}
    
    print(f"\n=== กำลังดึงข้อมูลพยากรณ์อากาศ 5 วัน ===")
    print(f"เมือง: {city_name}")
    
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',  # ใช้หน่วยเมตริก (องศาเซลเซียส)
        'lang': 'th',  # ใช้ภาษาไทย
        'cnt': 40  # จำนวนรายการพยากรณ์ (5 วัน * 8 รายการต่อวัน = 40 รายการ)
    }
    
    print(f"Forecast URL: {base_url}")
    print(f"Forecast Parameters: {params}")
    
    try:
        # ส่งคำขอไปยัง OpenWeatherMap API
        print("\n=== ส่งคำขอพยากรณ์อากาศไปยัง OpenWeatherMap ===")
        response = requests.get(base_url, params=params)
        
        # ตรวจสอบสถานะการตอบกลับ
        print(f"\n=== การตอบกลับจาก API พยากรณ์อากาศ ===")
        print(f"Status Code: {response.status_code}")
        
        # พยายามแปลงข้อมูล JSON
        data = response.json()
        print(f"Forecast Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")  # แสดงเฉพาะส่วนต้นของข้อมูล
        
        # ตรวจสอบสถานะการตอบกลับ
        if response.status_code != 200:
            error_msg = data.get('message', 'เกิดข้อผิดพลาดในการเชื่อมต่อกับ OpenWeatherMap API')
            print(f"Error: {error_msg}")
            return {'error': error_msg}
            
        print("\n=== ดึงข้อมูลพยากรณ์อากาศสำเร็จ ===")
        return data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}"
        print(f"Forecast Error: {error_msg}")
        return {'error': error_msg}
    except json.JSONDecodeError as e:
        error_msg = f"เกิดข้อผิดพลาดในการแปลงข้อมูล JSON: {str(e)}"
        print(f"Forecast JSON Error: {error_msg}")
        return {'error': 'เกิดข้อผิดพลาดในการประมวลผลข้อมูลพยากรณ์อากาศ'}
    except Exception as e:
        error_msg = f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {str(e)}"
        print(f"Forecast Error: {error_msg}")
        return {'error': 'เกิดข้อผิดพลาดในการดึงข้อมูลพยากรณ์อากาศ'}
    except requests.exceptions.RequestException as e:
        return {'error': 'เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์สภาพอากาศ'}
    except Exception as e:
        return {'error': f'เกิดข้อผิดพลาด: {str(e)}'}

def get_forecast(city_name, api_key):
    """
    ฟังก์ชันสำหรับดึงข้อมูลพยากรณ์อากาศ 5 วัน
    """
    if not api_key or api_key == 'your_api_key_here':
        return None
        
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',
        'lang': 'th',
        'cnt': 40  # จำนวนรายการ (5 วัน * 8 รายการต่อวัน)
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # ตรวจสอบว่ามีข้อมูลที่ถูกต้องหรือไม่
        if not data or 'list' not in data:
            return None
            
        return data
        
    except:
        return None

@app.route('/')
def home():
    """หน้าแรกของแอปพลิเคชัน"""
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
def weather():
    """API สำหรับดึงข้อมูลสภาพอากาศ"""
    city = request.args.get('city')
    
    if not city:
        return jsonify({'error': 'กรุณาระบุชื่อเมือง'}), 400
    
    if not API_KEY or API_KEY == 'your_api_key_here':
        return jsonify({'error': 'กรุณาตั้งค่า OpenWeatherMap API Key ในไฟล์ .env'}), 500
    
    try:
        # ดึงข้อมูลสภาพอากาศปัจจุบัน
        current_weather = get_weather(city, API_KEY)
        
        if 'error' in current_weather:
            return jsonify({'error': current_weather['error']}), 400
        
        # ดึงข้อมูลพยากรณ์อากาศ
        forecast = get_forecast(city, API_KEY)
        
        # สร้าง response ที่มีโครงสร้างที่ถูกต้อง
        response = {
            'name': current_weather.get('name', ''),
            'sys': current_weather.get('sys', {}),
            'main': current_weather.get('main', {}),
            'weather': current_weather.get('weather', []),
            'wind': current_weather.get('wind', {}),
            'visibility': current_weather.get('visibility', 0),
            'dt': current_weather.get('dt', 0),
            'timezone': current_weather.get('timezone', 0),
            'forecast': forecast.get('list', []) if forecast and 'list' in forecast else []
        }
        
        print("\n=== ส่งข้อมูลกลับไปยัง Frontend ===")
        print(f"มีข้อมูลพยากรณ์อากาศ: {len(response['forecast'])} รายการ")
        
        # ตรวจสอบว่า response มีข้อมูลที่จำเป็นหรือไม่
        if not all(key in response for key in ['main', 'weather', 'name', 'sys']):
            return jsonify({'error': 'ข้อมูลที่ได้รับจาก API ไม่ครบถ้วน'}), 500
            
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f'Error in weather API: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'เกิดข้อผิดพลาดในการประมวลผลคำขอ: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
