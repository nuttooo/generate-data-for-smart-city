from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from database import DatabaseConnection
from weather_simulator import WeatherSimulator
from smart_pole_simulator import SmartPoleSimulator
from power_meter_simulator import PowerMeterSimulator
from flow_meter_simulator import FlowMeterSimulator
import uvicorn

app = FastAPI(
    title="Smart City Data Generator API",
    description="REST API for managing and monitoring smart city IoT devices including smart poles, weather stations, power meters, and flow meters",
    version="1.0.0",
    contact={
        "name": "Smart City Team",
        "url": "https://github.com/nuttooo/generate-data-for-smart-city",
    }
)

# Database connection
db = DatabaseConnection()

# Pydantic models for request/response

class DeviceCategory(BaseModel):
    category_id: str
    category_name: str
    description: Optional[str] = None

class SmartPole(BaseModel):
    pole_id: str = Field(..., description="Unique identifier for the smart pole")
    location: str = Field(..., description="Location description")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    status: str = Field(default="on", pattern="^(on|off)$")

class SmartPoleModule(BaseModel):
    pole_id: str
    module_type: str = Field(..., description="Type: lighting, camera, sensor, wifi, display, charging")
    module_name: str
    power_rating_w: float = Field(..., gt=0)
    status: str = Field(default="active")

class PowerMeter(BaseModel):
    meter_id: str = Field(..., description="Unique identifier for the power meter")
    meter_type: str = Field(..., pattern="^(1-phase|3-phase)$")
    location: str
    room_name: Optional[str] = None
    building: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    status: str = Field(default="active")

class FlowMeter(BaseModel):
    meter_id: str = Field(..., description="Unique identifier for the flow meter")
    meter_type: str = Field(..., pattern="^(water|gas|steam|oil|air)$")
    flow_unit: str = Field(..., description="Flow rate unit: L/min, m3/h, kg/h, etc.")
    location: str
    building: Optional[str] = None
    pipe_size_mm: Optional[int] = Field(None, gt=0)
    max_flow_rate: Optional[float] = Field(None, gt=0)
    status: str = Field(default="active")

class ControlRequest(BaseModel):
    status: str = Field(..., pattern="^(on|off|active|inactive)$")

# Initialize database connection
@app.on_event("startup")
async def startup_event():
    db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    db.disconnect()

# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Smart City Data Generator API",
        "version": "1.0.0",
        "documentation": "/docs",
        "categories": [
            "Smart Poles",
            "Weather Stations",
            "Power Meters (1-phase & 3-phase)",
            "Flow Meters (Water, Gas, Steam, Air)"
        ]
    }

# Device Categories endpoints
@app.get("/categories", tags=["Device Categories"], response_model=List[Dict[str, Any]])
async def list_categories():
    """List all device categories"""
    query = "SELECT category_id, category_name, description FROM device_categories ORDER BY category_name"
    results = db.fetch_all(query)
    
    return [
        {
            "category_id": row[0],
            "category_name": row[1],
            "description": row[2]
        }
        for row in results
    ]

# Smart Pole endpoints
@app.get("/smart-poles", tags=["Smart Poles"])
async def list_smart_poles():
    """List all smart poles"""
    query = """
        SELECT pole_id, location, latitude, longitude, status, 
               created_at, updated_at
        FROM smart_poles
        ORDER BY pole_id
    """
    results = db.fetch_all(query)
    
    return [
        {
            "pole_id": row[0],
            "location": row[1],
            "latitude": float(row[2]) if row[2] else None,
            "longitude": float(row[3]) if row[3] else None,
            "status": row[4],
            "created_at": row[5].isoformat() if row[5] else None,
            "updated_at": row[6].isoformat() if row[6] else None
        }
        for row in results
    ]

@app.post("/smart-poles", tags=["Smart Poles"], status_code=201)
async def create_smart_pole(pole: SmartPole):
    """Create a new smart pole"""
    query = """
        INSERT INTO smart_poles (pole_id, location, latitude, longitude, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING pole_id
    """
    
    try:
        result = db.fetch_one(query, (
            pole.pole_id,
            pole.location,
            pole.latitude,
            pole.longitude,
            pole.status
        ))
        
        if result:
            return {"message": "Smart pole created successfully", "pole_id": result[0]}
        else:
            raise HTTPException(status_code=500, detail="Failed to create smart pole")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/smart-poles/{pole_id}", tags=["Smart Poles"])
async def get_smart_pole(pole_id: str):
    """Get details of a specific smart pole"""
    query = """
        SELECT pole_id, location, latitude, longitude, status, 
               created_at, updated_at
        FROM smart_poles
        WHERE pole_id = %s
    """
    result = db.fetch_one(query, (pole_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Smart pole not found")
    
    return {
        "pole_id": result[0],
        "location": result[1],
        "latitude": float(result[2]) if result[2] else None,
        "longitude": float(result[3]) if result[3] else None,
        "status": result[4],
        "created_at": result[5].isoformat() if result[5] else None,
        "updated_at": result[6].isoformat() if result[6] else None
    }

@app.put("/smart-poles/{pole_id}/control", tags=["Smart Poles"])
async def control_smart_pole(pole_id: str, control: ControlRequest):
    """Control smart pole (turn on/off)"""
    query = """
        UPDATE smart_poles 
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE pole_id = %s
        RETURNING pole_id, status
    """
    
    result = db.fetch_one(query, (control.status, pole_id))
    
    if not result:
        raise HTTPException(status_code=404, detail="Smart pole not found")
    
    return {
        "message": f"Smart pole {pole_id} status updated",
        "pole_id": result[0],
        "status": result[1]
    }

@app.delete("/smart-poles/{pole_id}", tags=["Smart Poles"])
async def delete_smart_pole(pole_id: str):
    """Delete a smart pole"""
    query = "DELETE FROM smart_poles WHERE pole_id = %s RETURNING pole_id"
    result = db.fetch_one(query, (pole_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Smart pole not found")
    
    return {"message": f"Smart pole {pole_id} deleted successfully"}

# Smart Pole Modules endpoints
@app.get("/smart-poles/{pole_id}/modules", tags=["Smart Poles"])
async def list_pole_modules(pole_id: str):
    """List all modules of a smart pole"""
    query = """
        SELECT module_type, module_name, power_rating_w, status
        FROM smart_pole_modules
        WHERE pole_id = %s
    """
    results = db.fetch_all(query, (pole_id,))
    
    return [
        {
            "module_type": row[0],
            "module_name": row[1],
            "power_rating_w": float(row[2]),
            "status": row[3]
        }
        for row in results
    ]

@app.post("/smart-poles/{pole_id}/modules", tags=["Smart Poles"], status_code=201)
async def add_pole_module(pole_id: str, module: SmartPoleModule):
    """Add a module to a smart pole"""
    # Verify pole exists
    pole_check = db.fetch_one("SELECT pole_id FROM smart_poles WHERE pole_id = %s", (pole_id,))
    if not pole_check:
        raise HTTPException(status_code=404, detail="Smart pole not found")
    
    query = """
        INSERT INTO smart_pole_modules (pole_id, module_type, module_name, power_rating_w, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    
    try:
        result = db.fetch_one(query, (
            pole_id,
            module.module_type,
            module.module_name,
            module.power_rating_w,
            module.status
        ))
        
        if result:
            return {"message": "Module added successfully", "module_id": result[0]}
        else:
            raise HTTPException(status_code=500, detail="Failed to add module")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Power Meter endpoints
@app.get("/power-meters", tags=["Power Meters"])
async def list_power_meters(meter_type: Optional[str] = Query(None, pattern="^(1-phase|3-phase)$")):
    """List all power meters, optionally filtered by type"""
    if meter_type:
        query = """
            SELECT meter_id, meter_type, location, room_name, building, 
                   latitude, longitude, status, created_at, updated_at
            FROM power_meters
            WHERE meter_type = %s
            ORDER BY meter_id
        """
        results = db.fetch_all(query, (meter_type,))
    else:
        query = """
            SELECT meter_id, meter_type, location, room_name, building, 
                   latitude, longitude, status, created_at, updated_at
            FROM power_meters
            ORDER BY meter_id
        """
        results = db.fetch_all(query)
    
    return [
        {
            "meter_id": row[0],
            "meter_type": row[1],
            "location": row[2],
            "room_name": row[3],
            "building": row[4],
            "latitude": float(row[5]) if row[5] else None,
            "longitude": float(row[6]) if row[6] else None,
            "status": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "updated_at": row[9].isoformat() if row[9] else None
        }
        for row in results
    ]

@app.post("/power-meters", tags=["Power Meters"], status_code=201)
async def create_power_meter(meter: PowerMeter):
    """Create a new power meter"""
    query = """
        INSERT INTO power_meters (meter_id, meter_type, location, room_name, building, 
                                  latitude, longitude, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING meter_id
    """
    
    try:
        result = db.fetch_one(query, (
            meter.meter_id,
            meter.meter_type,
            meter.location,
            meter.room_name,
            meter.building,
            meter.latitude,
            meter.longitude,
            meter.status
        ))
        
        if result:
            return {"message": "Power meter created successfully", "meter_id": result[0]}
        else:
            raise HTTPException(status_code=500, detail="Failed to create power meter")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/power-meters/{meter_id}", tags=["Power Meters"])
async def get_power_meter(meter_id: str):
    """Get details of a specific power meter"""
    query = """
        SELECT meter_id, meter_type, location, room_name, building, 
               latitude, longitude, status, created_at, updated_at
        FROM power_meters
        WHERE meter_id = %s
    """
    result = db.fetch_one(query, (meter_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Power meter not found")
    
    return {
        "meter_id": result[0],
        "meter_type": result[1],
        "location": result[2],
        "room_name": result[3],
        "building": result[4],
        "latitude": float(result[5]) if result[5] else None,
        "longitude": float(result[6]) if result[6] else None,
        "status": result[7],
        "created_at": result[8].isoformat() if result[8] else None,
        "updated_at": result[9].isoformat() if result[9] else None
    }

@app.get("/power-meters/{meter_id}/readings", tags=["Power Meters"])
async def get_power_meter_readings(
    meter_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of readings to return")
):
    """Get latest readings from a power meter"""
    query = """
        SELECT timestamp, voltage_v, current_a, power_w, power_factor, energy_kwh, 
               frequency_hz, voltage_l1_v, voltage_l2_v, voltage_l3_v,
               current_l1_a, current_l2_a, current_l3_a,
               power_l1_w, power_l2_w, power_l3_w
        FROM power_meter_readings
        WHERE meter_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    results = db.fetch_all(query, (meter_id, limit))
    
    return [
        {
            "timestamp": row[0].isoformat() if row[0] else None,
            "voltage_v": float(row[1]) if row[1] else None,
            "current_a": float(row[2]) if row[2] else None,
            "power_w": float(row[3]) if row[3] else None,
            "power_factor": float(row[4]) if row[4] else None,
            "energy_kwh": float(row[5]) if row[5] else None,
            "frequency_hz": float(row[6]) if row[6] else None,
            "three_phase": {
                "voltage_l1_v": float(row[7]) if row[7] else None,
                "voltage_l2_v": float(row[8]) if row[8] else None,
                "voltage_l3_v": float(row[9]) if row[9] else None,
                "current_l1_a": float(row[10]) if row[10] else None,
                "current_l2_a": float(row[11]) if row[11] else None,
                "current_l3_a": float(row[12]) if row[12] else None,
                "power_l1_w": float(row[13]) if row[13] else None,
                "power_l2_w": float(row[14]) if row[14] else None,
                "power_l3_w": float(row[15]) if row[15] else None,
            } if row[7] is not None else None
        }
        for row in results
    ]

@app.delete("/power-meters/{meter_id}", tags=["Power Meters"])
async def delete_power_meter(meter_id: str):
    """Delete a power meter"""
    query = "DELETE FROM power_meters WHERE meter_id = %s RETURNING meter_id"
    result = db.fetch_one(query, (meter_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Power meter not found")
    
    return {"message": f"Power meter {meter_id} deleted successfully"}

# Flow Meter endpoints
@app.get("/flow-meters", tags=["Flow Meters"])
async def list_flow_meters(meter_type: Optional[str] = Query(None, pattern="^(water|gas|steam|oil|air)$")):
    """List all flow meters, optionally filtered by type"""
    if meter_type:
        query = """
            SELECT meter_id, meter_type, flow_unit, location, building, 
                   pipe_size_mm, max_flow_rate, status, created_at, updated_at
            FROM flow_meters
            WHERE meter_type = %s
            ORDER BY meter_id
        """
        results = db.fetch_all(query, (meter_type,))
    else:
        query = """
            SELECT meter_id, meter_type, flow_unit, location, building, 
                   pipe_size_mm, max_flow_rate, status, created_at, updated_at
            FROM flow_meters
            ORDER BY meter_id
        """
        results = db.fetch_all(query)
    
    return [
        {
            "meter_id": row[0],
            "meter_type": row[1],
            "flow_unit": row[2],
            "location": row[3],
            "building": row[4],
            "pipe_size_mm": row[5],
            "max_flow_rate": float(row[6]) if row[6] else None,
            "status": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "updated_at": row[9].isoformat() if row[9] else None
        }
        for row in results
    ]

@app.post("/flow-meters", tags=["Flow Meters"], status_code=201)
async def create_flow_meter(meter: FlowMeter):
    """Create a new flow meter"""
    query = """
        INSERT INTO flow_meters (meter_id, meter_type, flow_unit, location, building,
                                pipe_size_mm, max_flow_rate, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING meter_id
    """
    
    try:
        result = db.fetch_one(query, (
            meter.meter_id,
            meter.meter_type,
            meter.flow_unit,
            meter.location,
            meter.building,
            meter.pipe_size_mm,
            meter.max_flow_rate,
            meter.status
        ))
        
        if result:
            return {"message": "Flow meter created successfully", "meter_id": result[0]}
        else:
            raise HTTPException(status_code=500, detail="Failed to create flow meter")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/flow-meters/{meter_id}", tags=["Flow Meters"])
async def get_flow_meter(meter_id: str):
    """Get details of a specific flow meter"""
    query = """
        SELECT meter_id, meter_type, flow_unit, location, building,
               pipe_size_mm, max_flow_rate, status, created_at, updated_at
        FROM flow_meters
        WHERE meter_id = %s
    """
    result = db.fetch_one(query, (meter_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Flow meter not found")
    
    return {
        "meter_id": result[0],
        "meter_type": result[1],
        "flow_unit": result[2],
        "location": result[3],
        "building": result[4],
        "pipe_size_mm": result[5],
        "max_flow_rate": float(result[6]) if result[6] else None,
        "status": result[7],
        "created_at": result[8].isoformat() if result[8] else None,
        "updated_at": result[9].isoformat() if result[9] else None
    }

@app.get("/flow-meters/{meter_id}/readings", tags=["Flow Meters"])
async def get_flow_meter_readings(
    meter_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of readings to return")
):
    """Get latest readings from a flow meter"""
    query = """
        SELECT timestamp, flow_rate, total_volume, temperature_c, pressure_bar, density
        FROM flow_meter_readings
        WHERE meter_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    results = db.fetch_all(query, (meter_id, limit))
    
    return [
        {
            "timestamp": row[0].isoformat() if row[0] else None,
            "flow_rate": float(row[1]) if row[1] else None,
            "total_volume": float(row[2]) if row[2] else None,
            "temperature_c": float(row[3]) if row[3] else None,
            "pressure_bar": float(row[4]) if row[4] else None,
            "density": float(row[5]) if row[5] else None
        }
        for row in results
    ]

@app.delete("/flow-meters/{meter_id}", tags=["Flow Meters"])
async def delete_flow_meter(meter_id: str):
    """Delete a flow meter"""
    query = "DELETE FROM flow_meters WHERE meter_id = %s RETURNING meter_id"
    result = db.fetch_one(query, (meter_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Flow meter not found")
    
    return {"message": f"Flow meter {meter_id} deleted successfully"}

# Weather Station endpoint
@app.get("/weather/latest", tags=["Weather Station"])
async def get_latest_weather():
    """Get latest weather station data"""
    query = """
        SELECT station_id, timestamp, temperature_c, humidity_percent, pressure_hpa,
               wind_speed_ms, wind_direction_deg, rainfall_mm, light_intensity_lux
        FROM weather_station
        ORDER BY timestamp DESC
        LIMIT 1
    """
    result = db.fetch_one(query)
    
    if not result:
        raise HTTPException(status_code=404, detail="No weather data available")
    
    return {
        "station_id": result[0],
        "timestamp": result[1].isoformat() if result[1] else None,
        "temperature_c": float(result[2]) if result[2] else None,
        "humidity_percent": float(result[3]) if result[3] else None,
        "pressure_hpa": float(result[4]) if result[4] else None,
        "wind_speed_ms": float(result[5]) if result[5] else None,
        "wind_direction_deg": result[6],
        "rainfall_mm": float(result[7]) if result[7] else None,
        "light_intensity_lux": result[8]
    }

# Statistics endpoints
@app.get("/statistics/power-consumption", tags=["Statistics"])
async def get_power_consumption_stats():
    """Get power consumption statistics across all meters"""
    query = """
        SELECT 
            pm.meter_type,
            COUNT(DISTINCT pm.meter_id) as meter_count,
            AVG(pmr.power_w) as avg_power_w,
            SUM(pmr.energy_kwh) as total_energy_kwh
        FROM power_meters pm
        LEFT JOIN power_meter_readings pmr ON pm.meter_id = pmr.meter_id
        WHERE pmr.timestamp >= NOW() - INTERVAL '1 hour'
        GROUP BY pm.meter_type
    """
    results = db.fetch_all(query)
    
    return [
        {
            "meter_type": row[0],
            "meter_count": row[1],
            "avg_power_w": float(row[2]) if row[2] else 0,
            "total_energy_kwh": float(row[3]) if row[3] else 0
        }
        for row in results
    ]

@app.get("/statistics/flow-rates", tags=["Statistics"])
async def get_flow_rate_stats():
    """Get flow rate statistics across all flow meters"""
    query = """
        SELECT 
            fm.meter_type,
            COUNT(DISTINCT fm.meter_id) as meter_count,
            AVG(fmr.flow_rate) as avg_flow_rate,
            SUM(fmr.total_volume) as total_volume
        FROM flow_meters fm
        LEFT JOIN flow_meter_readings fmr ON fm.meter_id = fmr.meter_id
        WHERE fmr.timestamp >= NOW() - INTERVAL '1 hour'
        GROUP BY fm.meter_type
    """
    results = db.fetch_all(query)
    
    return [
        {
            "meter_type": row[0],
            "meter_count": row[1],
            "avg_flow_rate": float(row[2]) if row[2] else 0,
            "total_volume": float(row[3]) if row[3] else 0
        }
        for row in results
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
