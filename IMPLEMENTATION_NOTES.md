# Implementation Notes

## Overview

This implementation provides a complete smart city data generation system that simulates realistic smart pole energy consumption and weather station data.

## Key Design Decisions

### 1. Module-Based Architecture

Each smart pole can have multiple modules (lighting, camera, sensors, WiFi, display, EV charging). Power consumption is calculated as the sum of all active modules plus overhead, allowing for realistic and flexible configuration.

### 2. Time-Based Variations

The system considers time of day for:
- **LED Lighting**: Adjusts based on ambient light intensity (measured in lux)
  - Full power at night when light < 10,000 lux
  - Reduced power during day when light > 50,000 lux
- **Digital Display**: Full power during active hours (6 AM - 10 PM), reduced at night
- **Weather**: Temperature and humidity follow natural daily cycles

### 3. Realistic Simulation

The simulation incorporates:
- **Random variations** specific to each module type
- **Weather correlation**: Light intensity affects lighting power consumption
- **Standby power**: OFF poles still consume 2W (realistic for control circuits)
- **EV charging variability**: Highly variable (0-100% utilization) to simulate real usage

### 4. Database Schema

Tables are normalized with proper relationships:
- `smart_poles`: Master table for pole information
- `smart_pole_modules`: Many-to-one relationship with poles
- `smart_pole_energy`: Time-series data for energy consumption
- `weather_station`: Time-series weather data

Indexes are added on frequently queried columns (pole_id, timestamp) for performance.

### 5. Bangkok Climate Profile

Weather simulation is tuned for Bangkok, Thailand:
- Base temperature: 28°C (range 25-35°C)
- Base humidity: 70% (range 50-95%)
- Tropical patterns with occasional rainfall

## Technical Highlights

### Power Calculation Formula

For each module:
```
actual_power = base_power × power_factor × random_factor

where:
- base_power: Module's rated power (from database)
- power_factor: Time/condition-based factor (0.1-1.0)
- random_factor: Module-specific variation (e.g., 1±0.15 for lighting)
```

Total pole power:
```
total_power = Σ(module_powers) + base_system_power
```

### Electrical Calculations

```python
voltage = 220-240V (realistic grid variation)
current = power / voltage
energy_kwh = power / 1000 (for 1-hour period)
```

### Time-Based Lighting Logic

```python
if daytime and light > 50000 lux:
    power_factor = 0.1  # 10% power
elif daytime and light > 20000 lux:
    power_factor = 0.3  # 30% power
elif daytime:
    power_factor = 0.7  # 70% power (cloudy)
else:  # nighttime
    power_factor = 1.0  # 100% power
```

## Usage Patterns

### For Development/Testing
```bash
python main.py generate  # Single cycle for quick tests
```

### For Demo/Presentation
```bash
python main.py continuous 30  # Generate every 30 seconds
```

### For Data Collection
```bash
python main.py continuous 60  # Generate every 60 seconds (production-like)
```

### For Control Testing
```bash
python main.py control SP001 off
python main.py generate
python main.py control SP001 on
python main.py generate
# Compare power consumption
```

## Extension Points

### Adding New Module Types

1. Add module type to database:
```sql
INSERT INTO smart_pole_modules (pole_id, module_type, module_name, power_rating_w)
VALUES ('SP001', 'new_type', 'New Module', 50.0);
```

2. Add variation factor in `smart_pole_simulator.py`:
```python
self.module_variations = {
    # existing types...
    'new_type': 0.10  # ±10% variation
}
```

3. Add custom logic if needed in `calculate_module_power()`.

### Adding New Smart Poles

Edit `init.sql` and add:
```sql
INSERT INTO smart_poles (pole_id, location, latitude, longitude, status) 
VALUES ('SP006', 'New Location', 13.123456, 100.123456, 'on');

INSERT INTO smart_pole_modules (pole_id, module_type, module_name, power_rating_w)
VALUES 
    ('SP006', 'lighting', 'LED Street Light', 120.0),
    ('SP006', 'camera', 'Security Camera', 15.0);
```

### Customizing Weather Patterns

Modify `weather_simulator.py`:
- Change `base_temperature`, `base_humidity`, `base_pressure` for different climates
- Adjust time-based formulas in `get_time_factor()`
- Modify ranges in each `generate_*()` method

## Performance Considerations

### Database

- Indexes on `(pole_id, timestamp)` enable fast time-range queries
- Consider partitioning `smart_pole_energy` table by timestamp for large datasets
- Regular VACUUM and ANALYZE for PostgreSQL optimization

### Data Generation

- Single cycle: ~1 second (5 poles + 1 weather station)
- Recommended interval: 30-60 seconds for continuous generation
- Can scale to hundreds of poles with minimal code changes

### Storage

Estimated storage per day (60-second interval):
- Energy data: ~1,440 rows × 5 poles = 7,200 rows (~500 KB)
- Weather data: ~1,440 rows (~100 KB)
- Total: ~600 KB/day or ~18 MB/month

## Testing

The automated test suite (`test.sh`) verifies:
1. All CLI commands work
2. Database connectivity
3. Data generation produces valid results
4. Control commands update database correctly
5. Queries return expected data

Run tests before and after changes:
```bash
./test.sh
```

## Security Considerations

- Database credentials in `.env` (not committed to git)
- `.env.example` provides template without sensitive data
- No direct SQL injection vectors (uses parameterized queries)
- Dependencies checked for vulnerabilities (all clear)

## Future Enhancements

Potential improvements:
1. **Web API**: RESTful API for remote monitoring and control
2. **Real-time Dashboard**: Web UI showing live data
3. **Alert System**: Notifications for anomalies (power spikes, sensor failures)
4. **Machine Learning**: Predict power consumption patterns
5. **Multiple Weather Stations**: Different locations with different conditions
6. **Energy Optimization**: Automatic control based on usage patterns
7. **Mobile App**: Control and monitoring from smartphones
8. **Export Features**: CSV/JSON export for external analysis

## Lessons Learned

1. **Module-based design** provides flexibility for different pole configurations
2. **Realistic variations** are crucial for believable simulation
3. **Time-based factors** make data patterns match real-world expectations
4. **Good documentation** is essential for usability
5. **Automated testing** catches issues early

## Credits

Implementation completed as part of the Smart City Data Generator project for realistic IoT simulation and testing.

## License

MIT License - Feel free to use and modify for your projects.
