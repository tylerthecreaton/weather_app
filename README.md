# Weather App

แอพตรวจสอบสภาพอากาศแบบง่ายๆ ด้วย Python และ OpenWeatherMap API

## วิธีการติดตั้ง

1. ติดตั้ง Python 3.6 ขึ้นไป
2. ติดตั้งไลบรารีที่จำเป็น:
   ```
   pip install -r requirements.txt
   ```
3. สร้างไฟล์ `.env` ในโฟลเดอร์โปรเจคและเพิ่ม OpenWeatherMap API Key ของคุณ:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

## วิธีการใช้งาน

รันโปรแกรมด้วยคำสั่ง:
```
python app.py
```

จากนั้นป้อนชื่อเมืองที่ต้องการตรวจสอบสภาพอากาศ

## วิธีรับ API Key

1. สมัครบัญชีที่ [OpenWeatherMap](https://openweathermap.org/)
2. ไปที่ [API keys](https://home.openweathermap.org/api_keys)
3. คัดลอก API Key ของคุณและนำไปใส่ในไฟล์ `.env`

## ฟีเจอร์

- ตรวจสอบสภาพอากาศตามชื่อเมือง
- แสดงอุณหภูมิ (เซลเซียส)
- แสดงสภาพอากาศโดยรวม
- แสดงความชื้นและความเร็วลม
- รองรับภาษาไทย
