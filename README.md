# Smart City Data Generator (Smart Pole Energy Simulator)

ระบบจำลองข้อมูลพลังงานสำหรับ Smart Pole และ Weather Station แบบเรียลไทม์

## ✨ Features / คุณสมบัติ

- 🔌 **จำลองการใช้พลังงานแบบเรียลไทม์** - จำลองค่าการใช้ไฟฟ้าของ Smart Pole ตามสภาพแวดล้อมจริง
- 💡 **Smart Pole Control** - สามารถเปิด/ปิด Smart Pole ได้แบบ Real-time
- 🌡️ **Weather Station Simulation** - จำลองข้อมูลสภาพอากาศแบบเรียลสติก (อุณหภูมิ, ความชื้น, ความเข้มแสง, ฯลฯ)
- 📦 **Module-based Power Consumption** - คำนวณพลังงานแยกตามโมดูลต่างๆ:
  - LED Street Light (ปรับตามความเข้มแสง)
  - Security Camera
  - Environmental Sensors
  - WiFi Access Point
  - Digital Display
  - EV Charging Station
- 🐘 **PostgreSQL Database** - เก็บข้อมูลด้วย PostgreSQL ผ่าน Docker
- 🐳 **Docker Support** - ติดตั้งและใช้งานง่ายด้วย Docker Compose

## 📋 Prerequisites / สิ่งที่ต้องมี

- Docker และ Docker Compose
- Python 3.8 หรือสูงกว่า
- pip (Python package manager)

## 🚀 Installation / การติดตั้ง

### 1. Clone Repository

```bash
git clone https://github.com/nuttooo/generate-data-for-smart-city.git
cd generate-data-for-smart-city
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
```

แก้ไข `.env` ตามต้องการ (ค่า default สามารถใช้งานได้เลย)

### 3. Start PostgreSQL Database

```bash
docker-compose up -d
```

รอจนกว่า database จะพร้อม (ประมาณ 10-15 วินาที)

```bash
docker-compose ps
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 📖 Usage / การใช้งาน

### Generate Single Data Cycle / สร้างข้อมูลครั้งเดียว

```bash
python main.py generate
```

### Continuous Data Generation / สร้างข้อมูลอย่างต่อเนื่อง

```bash
# Default: สร้างข้อมูลทุก 60 วินาที
python main.py continuous

# Custom interval: สร้างข้อมูลทุก 30 วินาที
python main.py continuous 30
```

### List All Smart Poles / ดูรายการ Smart Pole ทั้งหมด

```bash
python main.py list
```

### Control Smart Poles / ควบคุม Smart Pole

```bash
# เปิด Smart Pole
python main.py control SP001 on

# ปิด Smart Pole
python main.py control SP002 off

# สลับสถานะ (Toggle)
python main.py control SP003 toggle
```

### View Latest Data / ดูข้อมูลล่าสุด

```bash
python main.py view
```

## 🗄️ Database Schema / โครงสร้างฐานข้อมูล

### Tables / ตาราง

1. **smart_poles** - ข้อมูล Smart Pole
   - pole_id (unique identifier)
   - location (ตำแหน่ง)
   - latitude, longitude (พิกัด)
   - status (on/off)

2. **smart_pole_modules** - โมดูลต่างๆ ของ Smart Pole
   - pole_id (FK to smart_poles)
   - module_type (lighting, camera, sensor, wifi, display, charging)
   - power_rating_w (กำลังไฟฟ้าที่ใช้)

3. **smart_pole_energy** - ข้อมูลการใช้พลังงาน
   - pole_id (FK to smart_poles)
   - timestamp
   - power_consumption_w (กำลังไฟฟ้า Watts)
   - voltage_v (แรงดัน Volts)
   - current_a (กระแสไฟฟ้า Amperes)
   - energy_kwh (พลังงาน kWh)
   - status

4. **weather_station** - ข้อมูลสภาพอากาศ
   - station_id
   - timestamp
   - temperature_c (อุณหภูมิ °C)
   - humidity_percent (ความชื้น %)
   - pressure_hpa (ความกดอากาศ hPa)
   - wind_speed_ms (ความเร็วลม m/s)
   - wind_direction_deg (ทิศทางลม องศา)
   - rainfall_mm (ปริมาณฝน mm)
   - light_intensity_lux (ความเข้มแสง lux)

## 🔬 Realistic Simulation Features / ฟีเจอร์การจำลองแบบเรียลสติก

### 1. Time-based Power Consumption / การใช้พลังงานตามเวลา

- **LED Lighting**: ปรับกำลังไฟตามความเข้มแสงธรรมชาติ
  - กลางวัน (แสงสว่าง): ใช้ไฟ 10-30%
  - กลางคืน: ใช้ไฟ 100%
  
- **Digital Display**: ปรับตามช่วงเวลาใช้งาน
  - 06:00-22:00: ใช้ไฟเต็ม 100%
  - 22:00-06:00: ลดเหลือ 30%

- **EV Charging Station**: จำลองการใช้งานแบบสุ่ม (0-100%)

### 2. Weather-based Simulation / จำลองตามสภาพอากาศ

- อุณหภูมิเปลี่ยนตามเวลา (สูงสุดช่วง 14:00-15:00)
- ความชื้นสัมพันธ์ผกผันกับอุณหภูมิ
- ความเข้มแสงปรับตามเวลา (0-120,000 lux)
- ความกดอากาศและลมมีค่าเป็นไปตามธรรมชาติ

### 3. Module-specific Variations / ความแปรปรวนของแต่ละโมดูล

แต่ละโมดูลมีค่าความแปรปรวนที่แตกต่างกัน:
- Lighting: ±15%
- Camera: ±10%
- Sensors: ±5%
- WiFi: ±12%
- Display: ±20%
- Charging: ±30%

## 📊 Example Queries / ตัวอย่างคำสั่ง SQL

### ดูการใช้พลังงานรวมทั้งหมด

```sql
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    SUM(energy_kwh) as total_energy_kwh
FROM smart_pole_energy
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### ดูสถานะ Smart Pole ทั้งหมด

```sql
SELECT 
    sp.pole_id,
    sp.location,
    sp.status,
    COUNT(spm.id) as module_count,
    SUM(spm.power_rating_w) as total_power_rating
FROM smart_poles sp
LEFT JOIN smart_pole_modules spm ON sp.pole_id = spm.pole_id
GROUP BY sp.pole_id, sp.location, sp.status;
```

### ดูข้อมูลสภาพอากาศล่าสุด

```sql
SELECT *
FROM weather_station
ORDER BY timestamp DESC
LIMIT 10;
```

## 🛠️ Advanced Configuration / การตั้งค่าขั้นสูง

### Custom Smart Poles / เพิ่ม Smart Pole ใหม่

แก้ไขไฟล์ `init.sql` และเพิ่ม Smart Pole ใหม่:

```sql
INSERT INTO smart_poles (pole_id, location, latitude, longitude, status) 
VALUES ('SP006', 'New Location', 13.776717, 100.563186, 'on');
```

### Custom Modules / เพิ่มโมดูลใหม่

```sql
INSERT INTO smart_pole_modules (pole_id, module_type, module_name, power_rating_w)
VALUES ('SP006', 'custom', 'Custom Module', 50.0);
```

## 🧪 Testing / การทดสอบ

### Test Database Connection / ทดสอบการเชื่อมต่อฐานข้อมูล

```bash
docker-compose exec postgres psql -U admin -d smart_city -c "SELECT COUNT(*) FROM smart_poles;"
```

### Test Data Generation / ทดสอบการสร้างข้อมูล

```bash
python main.py generate
python main.py view
```

## 🐛 Troubleshooting / แก้ปัญหา

### Database Connection Error

```bash
# ตรวจสอบว่า PostgreSQL ทำงานอยู่
docker-compose ps

# ดู logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Module Not Found Error

```bash
# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt
```

## 📝 License

This project is open source and available under the MIT License.

## 👥 Contributors

- nuttooo

## 🙏 Acknowledgments

สร้างขึ้นเพื่อจำลองระบบ Smart City แบบเรียลไทม์สำหรับการศึกษาและพัฒนา