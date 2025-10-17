-- Example SQL queries for analyzing Smart City data

-- 1. Average power consumption per smart pole over time
SELECT 
    pole_id,
    AVG(power_consumption_w) as avg_power_w,
    MIN(power_consumption_w) as min_power_w,
    MAX(power_consumption_w) as max_power_w,
    COUNT(*) as sample_count
FROM smart_pole_energy
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY pole_id
ORDER BY avg_power_w DESC;

-- 2. Total energy consumption by hour
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    SUM(energy_kwh) as total_energy_kwh,
    AVG(power_consumption_w) as avg_power_w
FROM smart_pole_energy
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- 3. Smart pole status changes
SELECT 
    pole_id,
    status,
    COUNT(*) as status_count,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen
FROM smart_pole_energy
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY pole_id, status
ORDER BY pole_id, status;

-- 4. Weather correlation with power consumption
SELECT 
    DATE_TRUNC('minute', ws.timestamp) as time_minute,
    ws.temperature_c,
    ws.humidity_percent,
    ws.light_intensity_lux,
    AVG(spe.power_consumption_w) as avg_power_w
FROM weather_station ws
LEFT JOIN smart_pole_energy spe 
    ON DATE_TRUNC('minute', ws.timestamp) = DATE_TRUNC('minute', spe.timestamp)
WHERE ws.timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY time_minute, ws.temperature_c, ws.humidity_percent, ws.light_intensity_lux
ORDER BY time_minute DESC;

-- 5. Module inventory by smart pole
SELECT 
    sp.pole_id,
    sp.location,
    sp.status,
    COUNT(spm.id) as module_count,
    SUM(spm.power_rating_w) as total_rated_power_w,
    STRING_AGG(spm.module_type || ':' || spm.power_rating_w::text, ', ') as modules
FROM smart_poles sp
LEFT JOIN smart_pole_modules spm ON sp.pole_id = spm.pole_id
GROUP BY sp.pole_id, sp.location, sp.status
ORDER BY total_rated_power_w DESC;

-- 6. Power consumption efficiency (actual vs rated)
WITH pole_power AS (
    SELECT 
        sp.pole_id,
        SUM(spm.power_rating_w) as rated_power_w,
        (
            SELECT AVG(power_consumption_w)
            FROM smart_pole_energy spe
            WHERE spe.pole_id = sp.pole_id 
                AND spe.status = 'on'
                AND spe.timestamp >= NOW() - INTERVAL '1 hour'
        ) as avg_actual_power_w
    FROM smart_poles sp
    LEFT JOIN smart_pole_modules spm ON sp.pole_id = spm.pole_id
    GROUP BY sp.pole_id
)
SELECT 
    pole_id,
    rated_power_w,
    COALESCE(avg_actual_power_w, 0) as avg_actual_power_w,
    CASE 
        WHEN rated_power_w > 0 AND avg_actual_power_w IS NOT NULL 
        THEN ROUND((avg_actual_power_w / rated_power_w * 100)::numeric, 2)
        ELSE 0
    END as efficiency_percent
FROM pole_power
ORDER BY pole_id;

-- 7. Latest readings for all systems
SELECT 
    'Smart Pole' as system_type,
    pole_id as identifier,
    timestamp,
    power_consumption_w::text || 'W' as value,
    status
FROM smart_pole_energy
WHERE (pole_id, timestamp) IN (
    SELECT pole_id, MAX(timestamp)
    FROM smart_pole_energy
    GROUP BY pole_id
)
UNION ALL
SELECT 
    'Weather Station' as system_type,
    station_id as identifier,
    timestamp,
    temperature_c::text || '°C, ' || humidity_percent::text || '%, ' || light_intensity_lux::text || ' lux' as value,
    'active' as status
FROM weather_station
WHERE timestamp = (SELECT MAX(timestamp) FROM weather_station)
ORDER BY system_type, identifier;

-- 8. Energy cost estimation (assuming 4 THB per kWh)
SELECT 
    pole_id,
    SUM(energy_kwh) as total_energy_kwh,
    SUM(energy_kwh) * 4 as estimated_cost_thb,
    COUNT(*) as sample_count,
    MIN(timestamp) as period_start,
    MAX(timestamp) as period_end
FROM smart_pole_energy
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY pole_id
ORDER BY total_energy_kwh DESC;

-- 9. Module type performance analysis
SELECT 
    spm.module_type,
    COUNT(DISTINCT spm.pole_id) as pole_count,
    AVG(spm.power_rating_w) as avg_rated_power_w,
    SUM(spm.power_rating_w) as total_rated_power_w
FROM smart_pole_modules spm
WHERE spm.status = 'active'
GROUP BY spm.module_type
ORDER BY total_rated_power_w DESC;

-- 10. Hourly weather patterns
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour_of_day,
    AVG(temperature_c) as avg_temp_c,
    AVG(humidity_percent) as avg_humidity_pct,
    AVG(light_intensity_lux) as avg_light_lux,
    AVG(wind_speed_ms) as avg_wind_speed_ms,
    COUNT(*) as sample_count
FROM weather_station
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY hour_of_day
ORDER BY hour_of_day;
