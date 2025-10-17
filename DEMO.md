# Smart City Data Generator - Demo Guide

## Overview

This demo guide shows the complete functionality of the Smart City Data Generator system.

## Prerequisites

Make sure you have:
1. Docker and Docker Compose installed
2. Python 3.8+ installed
3. All dependencies installed (`pip install -r requirements.txt`)

## Step-by-Step Demo

### 1. Start the Database

```bash
docker compose up -d
```

Wait for the database to be healthy (about 10 seconds):

```bash
docker compose ps
```

You should see `healthy` in the status column.

### 2. Setup Environment

```bash
cp .env.example .env
```

The default settings work out of the box.

### 3. List All Smart Poles

```bash
python main.py list
```

**Expected Output:**
```
======================================================================
Pole ID    Location                  Status     Modules   
======================================================================
SP001      Main Street North         ON         5         
SP002      Central Avenue            ON         4         
SP003      Park Lane                 ON         3         
SP004      University Road           ON         6         
SP005      Business District         OFF        3         
======================================================================
```

**Observations:**
- 5 smart poles in different locations
- Each pole has different number of modules
- SP004 has the most modules (6) including an EV charging station
- SP005 starts in OFF state

### 4. Generate Single Data Cycle

```bash
python main.py generate
```

**Expected Output:**
```
============================================================
Generating data at 2025-10-17 06:37:41
============================================================
Weather data saved: Temp=28.83°C, Humidity=65.19%, Light=13557 lux
  SP001: ON - Power=218.67W, Energy=0.2187kWh
  SP002: ON - Power=127.15W, Energy=0.1272kWh
  SP003: ON - Power=104.08W, Energy=0.1041kWh
  SP004: ON - Power=225.08W, Energy=0.2251kWh
  SP005: OFF - Power=2.00W, Energy=0.0020kWh
```

**Observations:**
- Weather data is generated realistically
- Each ON pole consumes different power based on its modules
- SP005 (OFF) only uses 2W standby power
- SP004 typically has highest consumption due to EV charging station

### 5. View Latest Data

```bash
python main.py view
```

**Expected Output:**
```
======================================================================
Latest Weather Data
======================================================================
Temperature: 28.83°C
Humidity: 65.19%
Pressure: 1011.81 hPa
Wind Speed: 1.36 m/s
Rainfall: 0.00 mm
Light Intensity: 13557 lux
Timestamp: 2025-10-17 06:37:41.057580

======================================================================
Latest Smart Pole Energy Data
======================================================================
Pole ID    Status   Power (W)    Energy (kWh)   
----------------------------------------------------------------------
SP001      ON       218.67       0.2187         
SP002      ON       127.15       0.1272         
SP003      ON       104.08       0.1041         
SP004      ON       225.08       0.2251         
SP005      OFF      2.00         0.0020         
======================================================================
```

### 6. Control Smart Poles

#### Turn ON a pole:
```bash
python main.py control SP005 on
```

#### Turn OFF a pole:
```bash
python main.py control SP001 off
```

#### Toggle a pole:
```bash
python main.py control SP002 toggle
```

**Generate data again to see the effect:**
```bash
python main.py generate
```

Notice how power consumption changes based on pole status!

### 7. Continuous Data Generation

Generate data every 30 seconds:

```bash
python main.py continuous 30
```

**Output:**
```
Starting continuous data generation (interval: 30s)
Press Ctrl+C to stop

============================================================
Generating data at 2025-10-17 06:39:54
============================================================
Weather data saved: Temp=27.99°C, Humidity=71.74%, Light=5939 lux
  SP001: OFF - Power=2.00W, Energy=0.0020kWh
  SP002: ON - Power=130.18W, Energy=0.1302kWh
  SP003: ON - Power=106.11W, Energy=0.1061kWh
  SP004: ON - Power=359.02W, Energy=0.3590kWh
  SP005: ON - Power=116.07W, Energy=0.1161kWh

============================================================
Generating data at 2025-10-17 06:40:24
============================================================
Weather data saved: Temp=28.12°C, Humidity=69.43%, Light=6234 lux
...
```

Press Ctrl+C to stop.

### 8. Query the Database

#### Check total data points:
```bash
docker compose exec postgres psql -U admin -d smart_city -c \
  "SELECT COUNT(*) as total_records FROM smart_pole_energy;"
```

#### View recent weather data:
```bash
docker compose exec postgres psql -U admin -d smart_city -c \
  "SELECT timestamp, temperature_c, humidity_percent, light_intensity_lux 
   FROM weather_station 
   ORDER BY timestamp DESC 
   LIMIT 5;"
```

#### Analyze power consumption:
```bash
docker compose exec postgres psql -U admin -d smart_city -c \
  "SELECT pole_id, 
          AVG(power_consumption_w) as avg_power_w,
          MAX(power_consumption_w) as max_power_w,
          COUNT(*) as sample_count
   FROM smart_pole_energy
   WHERE timestamp >= NOW() - INTERVAL '1 hour'
   GROUP BY pole_id
   ORDER BY avg_power_w DESC;"
```

## Realistic Features Demonstrated

### 1. Time-based Power Variation

The LED lighting adjusts based on ambient light:
- **Daytime** (high light intensity): 10-30% power
- **Nighttime** (low light intensity): 100% power

Run the generator at different times to see this effect!

### 2. Module-specific Behavior

Different modules have different characteristics:
- **Lighting**: Varies with ambient light (±15%)
- **Camera**: Consistent draw (±10%)
- **Sensors**: Very stable (±5%)
- **WiFi**: Moderate variation (±12%)
- **Display**: Time-based (full power 6:00-22:00, reduced at night) (±20%)
- **EV Charging**: Highly variable based on usage (±30%)

### 3. Weather Simulation

Weather follows realistic patterns:
- Temperature peaks around 14:00-15:00
- Humidity inversely related to temperature
- Light intensity from 0 (night) to 120,000 lux (sunny day)
- Wind speed increases during daytime
- Occasional rainfall (10% probability)

### 4. Module Inventory

View what modules each pole has:

```bash
docker compose exec postgres psql -U admin -d smart_city -c \
  "SELECT pole_id, module_type, module_name, power_rating_w 
   FROM smart_pole_modules 
   WHERE pole_id = 'SP004' 
   ORDER BY power_rating_w DESC;"
```

SP004 output:
```
 pole_id | module_type |      module_name      | power_rating_w 
---------+-------------+-----------------------+----------------
 SP004   | charging    | EV Charging Station   |         350.00
 SP004   | lighting    | LED Street Light      |         120.00
 SP004   | display     | Digital Display       |          80.00
 SP004   | wifi        | WiFi Access Point     |          25.00
 SP004   | camera      | Security Camera       |          15.00
 SP004   | sensor      | Environmental Sensors |           5.00
```

## Example Analysis Queries

Use the example queries in `example_queries.sql`:

```bash
# Run any query from the file
docker compose exec postgres psql -U admin -d smart_city -f /path/to/example_queries.sql
```

Or run specific queries:

### Energy Cost Estimation (4 THB per kWh):
```sql
SELECT 
    pole_id,
    SUM(energy_kwh) as total_energy_kwh,
    SUM(energy_kwh) * 4 as estimated_cost_thb
FROM smart_pole_energy
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY pole_id
ORDER BY total_energy_kwh DESC;
```

### Weather Correlation:
```sql
SELECT 
    ws.light_intensity_lux,
    AVG(spe.power_consumption_w) as avg_power_w
FROM weather_station ws
JOIN smart_pole_energy spe 
    ON DATE_TRUNC('minute', ws.timestamp) = DATE_TRUNC('minute', spe.timestamp)
WHERE ws.timestamp >= NOW() - INTERVAL '1 hour'
    AND spe.pole_id = 'SP001'
GROUP BY ws.light_intensity_lux
ORDER BY ws.light_intensity_lux;
```

## Automated Testing

Run the complete test suite:

```bash
./test.sh
```

Expected output:
```
========================================
Smart City Data Generator - Test Suite
========================================

Test 1: Testing help command...
✓ Help command passed

Test 2: Listing smart poles...
✓ List poles passed

Test 3: Generating single data cycle...
✓ Generate data passed

...

========================================
All tests passed! ✓
========================================
```

## Tips for Best Results

1. **Generate data at different times of day** to see time-based variations
2. **Toggle poles on/off** to see the difference in power consumption
3. **Run continuous generation** for at least 5 minutes to collect meaningful data
4. **Use the example queries** to analyze patterns and correlations
5. **Monitor the database** using psql or a database client for real-time insights

## Cleanup

When done testing:

```bash
# Stop and remove containers
docker compose down

# Remove volumes (this will delete all data)
docker compose down -v
```

## Troubleshooting

### Database Connection Error
```bash
# Check if database is running
docker compose ps

# View logs
docker compose logs postgres

# Restart
docker compose restart
```

### Python Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Summary

This system demonstrates:
- ✅ Realistic energy simulation for smart poles
- ✅ Module-based power consumption calculation
- ✅ Weather station data generation
- ✅ Real-time control of smart poles (on/off)
- ✅ PostgreSQL data storage via Docker
- ✅ Time-based and weather-based variations
- ✅ Complete CLI interface for all operations
- ✅ SQL analysis capabilities

Perfect for smart city research, IoT demonstrations, and energy management system prototypes!
