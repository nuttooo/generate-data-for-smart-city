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
