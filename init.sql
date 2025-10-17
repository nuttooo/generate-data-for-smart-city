-- Create tables for smart city data

-- Table for smart pole information
CREATE TABLE IF NOT EXISTS smart_poles (
    id SERIAL PRIMARY KEY,
    pole_id VARCHAR(50) UNIQUE NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    status VARCHAR(20) DEFAULT 'on',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for smart pole energy consumption
CREATE TABLE IF NOT EXISTS smart_pole_energy (
    id SERIAL PRIMARY KEY,
    pole_id VARCHAR(50) REFERENCES smart_poles(pole_id),
    timestamp TIMESTAMP NOT NULL,
    power_consumption_w DECIMAL(10, 2) NOT NULL,
    voltage_v DECIMAL(10, 2) NOT NULL,
    current_a DECIMAL(10, 4) NOT NULL,
    energy_kwh DECIMAL(10, 4) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for weather station data
CREATE TABLE IF NOT EXISTS weather_station (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    temperature_c DECIMAL(5, 2),
    humidity_percent DECIMAL(5, 2),
    pressure_hpa DECIMAL(7, 2),
    wind_speed_ms DECIMAL(5, 2),
    wind_direction_deg INTEGER,
    rainfall_mm DECIMAL(6, 2),
    light_intensity_lux INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for smart pole modules (different components)
CREATE TABLE IF NOT EXISTS smart_pole_modules (
    id SERIAL PRIMARY KEY,
    pole_id VARCHAR(50) REFERENCES smart_poles(pole_id),
    module_type VARCHAR(50) NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    power_rating_w DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_energy_pole_timestamp ON smart_pole_energy(pole_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_station(timestamp);
CREATE INDEX IF NOT EXISTS idx_modules_pole ON smart_pole_modules(pole_id);

-- Insert sample smart poles
INSERT INTO smart_poles (pole_id, location, latitude, longitude, status) VALUES
    ('SP001', 'Main Street North', 13.736717, 100.523186, 'on'),
    ('SP002', 'Central Avenue', 13.746717, 100.533186, 'on'),
    ('SP003', 'Park Lane', 13.726717, 100.513186, 'on'),
    ('SP004', 'University Road', 13.756717, 100.543186, 'on'),
    ('SP005', 'Business District', 13.766717, 100.553186, 'off')
ON CONFLICT (pole_id) DO NOTHING;

-- Insert sample modules for each smart pole
INSERT INTO smart_pole_modules (pole_id, module_type, module_name, power_rating_w) VALUES
    ('SP001', 'lighting', 'LED Street Light', 120.0),
    ('SP001', 'camera', 'Security Camera', 15.0),
    ('SP001', 'sensor', 'Environmental Sensors', 5.0),
    ('SP001', 'wifi', 'WiFi Access Point', 25.0),
    ('SP001', 'display', 'Digital Display', 80.0),
    ('SP002', 'lighting', 'LED Street Light', 120.0),
    ('SP002', 'camera', 'Security Camera', 15.0),
    ('SP002', 'sensor', 'Environmental Sensors', 5.0),
    ('SP002', 'wifi', 'WiFi Access Point', 25.0),
    ('SP003', 'lighting', 'LED Street Light', 120.0),
    ('SP003', 'camera', 'Security Camera', 15.0),
    ('SP003', 'sensor', 'Environmental Sensors', 5.0),
    ('SP004', 'lighting', 'LED Street Light', 120.0),
    ('SP004', 'camera', 'Security Camera', 15.0),
    ('SP004', 'sensor', 'Environmental Sensors', 5.0),
    ('SP004', 'wifi', 'WiFi Access Point', 25.0),
    ('SP004', 'display', 'Digital Display', 80.0),
    ('SP004', 'charging', 'EV Charging Station', 350.0),
    ('SP005', 'lighting', 'LED Street Light', 120.0),
    ('SP005', 'camera', 'Security Camera', 15.0),
    ('SP005', 'sensor', 'Environmental Sensors', 5.0)
ON CONFLICT DO NOTHING;

-- Insert initial weather station
INSERT INTO weather_station (station_id, timestamp, temperature_c, humidity_percent, pressure_hpa, wind_speed_ms, wind_direction_deg, rainfall_mm, light_intensity_lux)
VALUES ('WS001', CURRENT_TIMESTAMP, 28.5, 65.0, 1013.25, 2.5, 180, 0.0, 50000)
ON CONFLICT DO NOTHING;

-- Table for device categories
CREATE TABLE IF NOT EXISTS device_categories (
    id SERIAL PRIMARY KEY,
    category_id VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for power meters (1-phase and 3-phase)
CREATE TABLE IF NOT EXISTS power_meters (
    id SERIAL PRIMARY KEY,
    meter_id VARCHAR(50) UNIQUE NOT NULL,
    meter_type VARCHAR(20) NOT NULL, -- '1-phase' or '3-phase'
    location VARCHAR(255) NOT NULL,
    room_name VARCHAR(100),
    building VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for power meter readings
CREATE TABLE IF NOT EXISTS power_meter_readings (
    id SERIAL PRIMARY KEY,
    meter_id VARCHAR(50) REFERENCES power_meters(meter_id),
    timestamp TIMESTAMP NOT NULL,
    voltage_v DECIMAL(10, 2) NOT NULL,
    current_a DECIMAL(10, 4) NOT NULL,
    power_w DECIMAL(10, 2) NOT NULL,
    power_factor DECIMAL(5, 3),
    energy_kwh DECIMAL(10, 4) NOT NULL,
    frequency_hz DECIMAL(5, 2),
    -- For 3-phase specific
    voltage_l1_v DECIMAL(10, 2),
    voltage_l2_v DECIMAL(10, 2),
    voltage_l3_v DECIMAL(10, 2),
    current_l1_a DECIMAL(10, 4),
    current_l2_a DECIMAL(10, 4),
    current_l3_a DECIMAL(10, 4),
    power_l1_w DECIMAL(10, 2),
    power_l2_w DECIMAL(10, 2),
    power_l3_w DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for flow meters
CREATE TABLE IF NOT EXISTS flow_meters (
    id SERIAL PRIMARY KEY,
    meter_id VARCHAR(50) UNIQUE NOT NULL,
    meter_type VARCHAR(50) NOT NULL, -- 'water', 'gas', 'steam', 'oil', 'air'
    flow_unit VARCHAR(20) NOT NULL, -- 'L/min', 'm3/h', 'kg/h', etc.
    location VARCHAR(255) NOT NULL,
    building VARCHAR(100),
    pipe_size_mm INTEGER,
    max_flow_rate DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for flow meter readings
CREATE TABLE IF NOT EXISTS flow_meter_readings (
    id SERIAL PRIMARY KEY,
    meter_id VARCHAR(50) REFERENCES flow_meters(meter_id),
    timestamp TIMESTAMP NOT NULL,
    flow_rate DECIMAL(10, 3) NOT NULL,
    total_volume DECIMAL(15, 3) NOT NULL,
    temperature_c DECIMAL(5, 2),
    pressure_bar DECIMAL(7, 2),
    density DECIMAL(7, 3), -- For mass flow meters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_power_meter_readings_timestamp ON power_meter_readings(meter_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_flow_meter_readings_timestamp ON flow_meter_readings(meter_id, timestamp);

-- Insert device categories
INSERT INTO device_categories (category_id, category_name, description) VALUES
    ('smart_pole', 'Smart Pole', 'Smart street lighting poles with IoT modules'),
    ('weather_station', 'Weather Station', 'Environmental monitoring stations'),
    ('power_meter_1ph', 'Power Meter 1-Phase', 'Single-phase power meters for room/zone monitoring'),
    ('power_meter_3ph', 'Power Meter 3-Phase', 'Three-phase power meters for building/facility monitoring'),
    ('flow_meter_water', 'Water Flow Meter', 'Water consumption monitoring'),
    ('flow_meter_gas', 'Gas Flow Meter', 'Gas flow monitoring'),
    ('flow_meter_steam', 'Steam Flow Meter', 'Steam flow monitoring'),
    ('flow_meter_air', 'Air Flow Meter', 'Compressed air flow monitoring')
ON CONFLICT (category_id) DO NOTHING;

-- Insert sample power meters (1-phase for rooms)
INSERT INTO power_meters (meter_id, meter_type, location, room_name, building, latitude, longitude, status) VALUES
    ('PM1P001', '1-phase', 'Building A - Room 101', 'Room 101', 'Building A', 13.736717, 100.523186, 'active'),
    ('PM1P002', '1-phase', 'Building A - Room 102', 'Room 102', 'Building A', 13.736717, 100.523186, 'active'),
    ('PM1P003', '1-phase', 'Building A - Room 201', 'Room 201', 'Building A', 13.736717, 100.523186, 'active'),
    ('PM1P004', '1-phase', 'Building B - Office 1', 'Office 1', 'Building B', 13.746717, 100.533186, 'active'),
    ('PM1P005', '1-phase', 'Building B - Office 2', 'Office 2', 'Building B', 13.746717, 100.533186, 'active')
ON CONFLICT (meter_id) DO NOTHING;

-- Insert sample power meters (3-phase for buildings)
INSERT INTO power_meters (meter_id, meter_type, location, room_name, building, latitude, longitude, status) VALUES
    ('PM3P001', '3-phase', 'Building A - Main Distribution', 'Main Panel', 'Building A', 13.736717, 100.523186, 'active'),
    ('PM3P002', '3-phase', 'Building B - Main Distribution', 'Main Panel', 'Building B', 13.746717, 100.533186, 'active'),
    ('PM3P003', '3-phase', 'Building C - Main Distribution', 'Main Panel', 'Building C', 13.756717, 100.543186, 'active')
ON CONFLICT (meter_id) DO NOTHING;

-- Insert sample flow meters
INSERT INTO flow_meters (meter_id, meter_type, flow_unit, location, building, pipe_size_mm, max_flow_rate, status) VALUES
    ('FM_W001', 'water', 'L/min', 'Building A - Water Supply', 'Building A', 50, 100.0, 'active'),
    ('FM_W002', 'water', 'L/min', 'Building B - Water Supply', 'Building B', 50, 100.0, 'active'),
    ('FM_W003', 'water', 'm3/h', 'Main Water Line', 'Campus', 100, 50.0, 'active'),
    ('FM_G001', 'gas', 'm3/h', 'Building A - Gas Line', 'Building A', 25, 20.0, 'active'),
    ('FM_G002', 'gas', 'm3/h', 'Cafeteria - Gas Supply', 'Cafeteria', 32, 30.0, 'active'),
    ('FM_S001', 'steam', 'kg/h', 'Central Boiler - Steam', 'Boiler Room', 80, 500.0, 'active'),
    ('FM_A001', 'air', 'm3/min', 'Compressor Station', 'Workshop', 40, 15.0, 'active'),
    ('FM_A002', 'air', 'm3/min', 'Production Line', 'Factory', 50, 25.0, 'active')
ON CONFLICT (meter_id) DO NOTHING;
