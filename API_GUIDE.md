# Smart City API Guide

## Overview

The Smart City Data Generator now includes a comprehensive REST API built with FastAPI, featuring automatic Swagger documentation.

## Starting the API Server

```bash
python main.py api
```

The API will start on `http://localhost:8000`

## Documentation URLs

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc (Alternative)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Device Categories

#### `GET /categories`
List all device categories

**Response:**
```json
[
  {
    "category_id": "power_meter_1ph",
    "category_name": "Power Meter 1-Phase",
    "description": "Single-phase power meters for room/zone monitoring"
  }
]
```

### Smart Poles

#### `GET /smart-poles`
List all smart poles

#### `POST /smart-poles`
Create a new smart pole

**Request Body:**
```json
{
  "pole_id": "SP006",
  "location": "New Street",
  "latitude": 13.736717,
  "longitude": 100.523186,
  "status": "on"
}
```

#### `GET /smart-poles/{pole_id}`
Get details of a specific smart pole

#### `PUT /smart-poles/{pole_id}/control`
Control smart pole (turn on/off)

**Request Body:**
```json
{
  "status": "on"
}
```

#### `DELETE /smart-poles/{pole_id}`
Delete a smart pole

#### `GET /smart-poles/{pole_id}/modules`
List all modules of a smart pole

#### `POST /smart-poles/{pole_id}/modules`
Add a module to a smart pole

**Request Body:**
```json
{
  "pole_id": "SP001",
  "module_type": "lighting",
  "module_name": "LED Street Light",
  "power_rating_w": 120.0,
  "status": "active"
}
```

### Power Meters

#### `GET /power-meters?meter_type=1-phase`
List all power meters (optionally filter by type)

Query Parameters:
- `meter_type` (optional): `1-phase` or `3-phase`

#### `POST /power-meters`
Create a new power meter

**Request Body (1-Phase):**
```json
{
  "meter_id": "PM1P006",
  "meter_type": "1-phase",
  "location": "Building A - Room 301",
  "room_name": "Room 301",
  "building": "Building A",
  "latitude": 13.736717,
  "longitude": 100.523186,
  "status": "active"
}
```

**Request Body (3-Phase):**
```json
{
  "meter_id": "PM3P004",
  "meter_type": "3-phase",
  "location": "Building D - Main Distribution",
  "room_name": "Main Panel",
  "building": "Building D",
  "status": "active"
}
```

#### `GET /power-meters/{meter_id}`
Get details of a specific power meter

#### `GET /power-meters/{meter_id}/readings?limit=10`
Get latest readings from a power meter

Query Parameters:
- `limit` (optional, default: 10, max: 100): Number of readings to return

**Response Example (3-Phase):**
```json
[
  {
    "timestamp": "2025-10-17T10:34:49.274835",
    "voltage_v": 231.25,
    "current_a": 65.4321,
    "power_w": 14576.64,
    "power_factor": 0.923,
    "energy_kwh": 14.5766,
    "frequency_hz": 50.02,
    "three_phase": {
      "voltage_l1_v": 230.45,
      "voltage_l2_v": 231.89,
      "voltage_l3_v": 231.41,
      "current_l1_a": 21.8234,
      "current_l2_a": 21.7543,
      "current_l3_a": 21.8544,
      "power_l1_w": 4862.21,
      "power_l2_w": 4857.22,
      "power_l3_w": 4857.21
    }
  }
]
```

#### `DELETE /power-meters/{meter_id}`
Delete a power meter

### Flow Meters

#### `GET /flow-meters?meter_type=water`
List all flow meters (optionally filter by type)

Query Parameters:
- `meter_type` (optional): `water`, `gas`, `steam`, `air`

#### `POST /flow-meters`
Create a new flow meter

**Request Body (Water):**
```json
{
  "meter_id": "FM_W004",
  "meter_type": "water",
  "flow_unit": "L/min",
  "location": "Building C - Water Supply",
  "building": "Building C",
  "pipe_size_mm": 50,
  "max_flow_rate": 100.0,
  "status": "active"
}
```

**Request Body (Gas):**
```json
{
  "meter_id": "FM_G003",
  "meter_type": "gas",
  "flow_unit": "m3/h",
  "location": "Laboratory - Gas Line",
  "building": "Lab Building",
  "pipe_size_mm": 25,
  "max_flow_rate": 20.0,
  "status": "active"
}
```

**Request Body (Steam):**
```json
{
  "meter_id": "FM_S002",
  "meter_type": "steam",
  "flow_unit": "kg/h",
  "location": "Process Steam Line",
  "building": "Factory",
  "pipe_size_mm": 80,
  "max_flow_rate": 500.0,
  "status": "active"
}
```

**Request Body (Air):**
```json
{
  "meter_id": "FM_A003",
  "meter_type": "air",
  "flow_unit": "m3/min",
  "location": "Pneumatic System",
  "building": "Workshop",
  "pipe_size_mm": 40,
  "max_flow_rate": 15.0,
  "status": "active"
}
```

#### `GET /flow-meters/{meter_id}`
Get details of a specific flow meter

#### `GET /flow-meters/{meter_id}/readings?limit=10`
Get latest readings from a flow meter

**Response Example:**
```json
[
  {
    "timestamp": "2025-10-17T10:34:49.324567",
    "flow_rate": 36.752,
    "total_volume": 36.752,
    "temperature_c": 22.45,
    "pressure_bar": 3.25,
    "density": null
  }
]
```

#### `DELETE /flow-meters/{meter_id}`
Delete a flow meter

### Weather Station

#### `GET /weather/latest`
Get latest weather station data

**Response:**
```json
{
  "station_id": "WS001",
  "timestamp": "2025-10-17T10:34:49.218654",
  "temperature_c": 31.02,
  "humidity_percent": 58.85,
  "pressure_hpa": 1013.14,
  "wind_speed_ms": 3.56,
  "wind_direction_deg": 245,
  "rainfall_mm": 0.0,
  "light_intensity_lux": 80026
}
```

### Statistics

#### `GET /statistics/power-consumption`
Get power consumption statistics across all meters

**Response:**
```json
[
  {
    "meter_type": "1-phase",
    "meter_count": 5,
    "avg_power_w": 1071.97,
    "total_energy_kwh": 5.3599
  },
  {
    "meter_type": "3-phase",
    "meter_count": 3,
    "avg_power_w": 15362.99,
    "total_energy_kwh": 46.0963
  }
]
```

#### `GET /statistics/flow-rates`
Get flow rate statistics across all flow meters

**Response:**
```json
[
  {
    "meter_type": "water",
    "meter_count": 3,
    "avg_flow_rate": 28.864,
    "total_volume": 86.593
  },
  {
    "meter_type": "gas",
    "meter_count": 2,
    "avg_flow_rate": 8.439,
    "total_volume": 0.281
  }
]
```

## Example Usage with curl

### List all device categories
```bash
curl http://localhost:8000/categories
```

### Create a new 1-phase power meter
```bash
curl -X POST http://localhost:8000/power-meters \
  -H "Content-Type: application/json" \
  -d '{
    "meter_id": "PM1P006",
    "meter_type": "1-phase",
    "location": "Room 301",
    "room_name": "Room 301",
    "building": "Building A",
    "status": "active"
  }'
```

### Create a new water flow meter
```bash
curl -X POST http://localhost:8000/flow-meters \
  -H "Content-Type: application/json" \
  -d '{
    "meter_id": "FM_W004",
    "meter_type": "water",
    "flow_unit": "L/min",
    "location": "Building C",
    "building": "Building C",
    "pipe_size_mm": 50,
    "max_flow_rate": 100.0,
    "status": "active"
  }'
```

### Get latest power meter readings
```bash
curl http://localhost:8000/power-meters/PM3P001/readings?limit=5
```

### Control a smart pole
```bash
curl -X PUT http://localhost:8000/smart-poles/SP001/control \
  -H "Content-Type: application/json" \
  -d '{"status": "off"}'
```

### Get power consumption statistics
```bash
curl http://localhost:8000/statistics/power-consumption
```

## Example Usage with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# List all power meters
response = requests.get(f"{BASE_URL}/power-meters")
power_meters = response.json()
print(f"Found {len(power_meters)} power meters")

# Create a new flow meter
new_meter = {
    "meter_id": "FM_W005",
    "meter_type": "water",
    "flow_unit": "L/min",
    "location": "New Building - Water",
    "building": "New Building",
    "status": "active"
}
response = requests.post(f"{BASE_URL}/flow-meters", json=new_meter)
print(response.json())

# Get latest weather data
response = requests.get(f"{BASE_URL}/weather/latest")
weather = response.json()
print(f"Temperature: {weather['temperature_c']}°C")

# Get power meter readings
response = requests.get(f"{BASE_URL}/power-meters/PM3P001/readings?limit=10")
readings = response.json()
for reading in readings:
    print(f"Power: {reading['power_w']}W, Time: {reading['timestamp']}")
```

## Interactive Testing with Swagger UI

1. Start the API server:
   ```bash
   python main.py api
   ```

2. Open browser to http://localhost:8000/docs

3. You'll see an interactive interface where you can:
   - Expand any endpoint to see details
   - Click "Try it out" to test the endpoint
   - Fill in parameters and request body
   - Click "Execute" to send the request
   - View the response

4. Authentication is not required for this API (can be added if needed)

## Error Responses

### 404 Not Found
```json
{
  "detail": "Smart pole not found"
}
```

### 400 Bad Request
```json
{
  "detail": "duplicate key value violates unique constraint"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to create power meter"
}
```

## API Features

- ✅ Full CRUD operations for all device types
- ✅ Automatic request/response validation with Pydantic
- ✅ Interactive Swagger UI documentation
- ✅ Alternative ReDoc documentation
- ✅ Query parameter filtering
- ✅ Pagination support for readings
- ✅ Proper HTTP status codes
- ✅ Error handling with detailed messages
- ✅ JSON request/response format

## Tips

1. **Use Swagger UI** for quick testing and exploration
2. **Check response schemas** in the documentation before integrating
3. **Filter by meter type** when listing power meters or flow meters
4. **Set appropriate limits** when fetching readings to avoid large responses
5. **Use the statistics endpoints** for aggregated data

## Future Enhancements

Potential additions:
- Authentication & Authorization
- WebSocket support for real-time data
- Bulk operations (create multiple devices at once)
- Data export endpoints (CSV, Excel)
- Advanced filtering and sorting
- GraphQL endpoint as alternative to REST
