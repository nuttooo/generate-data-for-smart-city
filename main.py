from datetime import datetime
from database import DatabaseConnection
from weather_simulator import WeatherSimulator
from smart_pole_simulator import SmartPoleSimulator
from power_meter_simulator import PowerMeterSimulator
from flow_meter_simulator import FlowMeterSimulator
import time
import sys

class SmartCityDataGenerator:
    """Main application to generate and store smart city data"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.weather_sim = WeatherSimulator()
        self.pole_sim = None
        self.power_meter_sim = None
        self.flow_meter_sim = None
        
    def connect_database(self):
        """Connect to database"""
        return self.db.connect()
    
    def initialize(self):
        """Initialize the system"""
        if not self.connect_database():
            print("Failed to connect to database. Make sure PostgreSQL is running.")
            return False
        
        self.pole_sim = SmartPoleSimulator(self.db)
        self.power_meter_sim = PowerMeterSimulator(self.db)
        self.flow_meter_sim = FlowMeterSimulator(self.db)
        print("Smart City Data Generator initialized successfully")
        return True
    
    def save_weather_data(self, station_id='WS001'):
        """Generate and save weather station data"""
        weather_data = self.weather_sim.generate_weather_data()
        
        query = """
            INSERT INTO weather_station 
            (station_id, timestamp, temperature_c, humidity_percent, pressure_hpa, 
             wind_speed_ms, wind_direction_deg, rainfall_mm, light_intensity_lux)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            station_id,
            datetime.now(),
            weather_data['temperature_c'],
            weather_data['humidity_percent'],
            weather_data['pressure_hpa'],
            weather_data['wind_speed_ms'],
            weather_data['wind_direction_deg'],
            weather_data['rainfall_mm'],
            weather_data['light_intensity_lux']
        )
        
        if self.db.execute_query(query, params):
            print(f"Weather data saved: Temp={weather_data['temperature_c']}°C, "
                  f"Humidity={weather_data['humidity_percent']}%, "
                  f"Light={weather_data['light_intensity_lux']} lux")
            return weather_data
        return None
    
    def save_pole_energy_data(self, pole_id, energy_data):
        """Save smart pole energy data"""
        query = """
            INSERT INTO smart_pole_energy 
            (pole_id, timestamp, power_consumption_w, voltage_v, current_a, 
             energy_kwh, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            pole_id,
            datetime.now(),
            energy_data['power_consumption_w'],
            energy_data['voltage_v'],
            energy_data['current_a'],
            energy_data['energy_kwh'],
            energy_data['status']
        )
        
        return self.db.execute_query(query, params)
    
    def save_power_meter_data(self, meter_id, reading_data):
        """Save power meter reading data"""
        query = """
            INSERT INTO power_meter_readings 
            (meter_id, timestamp, voltage_v, current_a, power_w, power_factor, 
             energy_kwh, frequency_hz, voltage_l1_v, voltage_l2_v, voltage_l3_v,
             current_l1_a, current_l2_a, current_l3_a,
             power_l1_w, power_l2_w, power_l3_w)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            meter_id,
            datetime.now(),
            reading_data['voltage_v'],
            reading_data['current_a'],
            reading_data['power_w'],
            reading_data['power_factor'],
            reading_data['energy_kwh'],
            reading_data['frequency_hz'],
            reading_data['voltage_l1_v'],
            reading_data['voltage_l2_v'],
            reading_data['voltage_l3_v'],
            reading_data['current_l1_a'],
            reading_data['current_l2_a'],
            reading_data['current_l3_a'],
            reading_data['power_l1_w'],
            reading_data['power_l2_w'],
            reading_data['power_l3_w']
        )
        
        return self.db.execute_query(query, params)
    
    def save_flow_meter_data(self, meter_id, reading_data):
        """Save flow meter reading data"""
        query = """
            INSERT INTO flow_meter_readings 
            (meter_id, timestamp, flow_rate, total_volume, temperature_c, pressure_bar, density)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            meter_id,
            datetime.now(),
            reading_data['flow_rate'],
            reading_data['total_volume'],
            reading_data['temperature_c'],
            reading_data['pressure_bar'],
            reading_data['density']
        )
        
        return self.db.execute_query(query, params)
    
    def generate_cycle(self):
        """Generate one cycle of data for all systems"""
        print(f"\n{'='*70}")
        print(f"Generating data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Generate weather data
        weather_data = self.save_weather_data()
        
        if weather_data:
            # Generate energy data for all smart poles
            print("\n[Smart Poles]")
            poles = self.pole_sim.get_all_poles()
            
            for pole_id in poles:
                energy_data = self.pole_sim.generate_energy_data(pole_id, weather_data)
                if self.save_pole_energy_data(pole_id, energy_data):
                    print(f"  {pole_id}: {energy_data['status'].upper()} - "
                          f"Power={energy_data['power_consumption_w']:.2f}W, "
                          f"Energy={energy_data['energy_kwh']:.4f}kWh")
            
            # Generate power meter readings
            print("\n[Power Meters]")
            power_meters = self.power_meter_sim.get_all_meters()
            
            for meter_id in power_meters:
                reading_data = self.power_meter_sim.generate_reading(meter_id)
                if reading_data and self.save_power_meter_data(meter_id, reading_data):
                    meter_info = self.power_meter_sim.get_meter_info(meter_id)
                    print(f"  {meter_id} ({meter_info['meter_type']}): "
                          f"Power={reading_data['power_w']:.2f}W, "
                          f"Energy={reading_data['energy_kwh']:.4f}kWh")
            
            # Generate flow meter readings
            print("\n[Flow Meters]")
            flow_meters = self.flow_meter_sim.get_all_meters()
            
            for meter_id in flow_meters:
                reading_data = self.flow_meter_sim.generate_reading(meter_id)
                if reading_data and self.save_flow_meter_data(meter_id, reading_data):
                    meter_info = self.flow_meter_sim.get_meter_info(meter_id)
                    print(f"  {meter_id} ({meter_info['meter_type']}): "
                          f"Flow={reading_data['flow_rate']:.3f} {meter_info['flow_unit']}, "
                          f"Total={reading_data['total_volume']:.3f}")

    
    def run_continuous(self, interval_seconds=60):
        """Run continuous data generation"""
        print(f"\nStarting continuous data generation (interval: {interval_seconds}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.generate_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\nStopping data generation...")
            self.cleanup()
    
    def run_single(self):
        """Run single data generation cycle"""
        self.generate_cycle()
        self.cleanup()
    
    def control_pole(self, pole_id, action):
        """Control smart pole (on/off/toggle)"""
        if action == 'toggle':
            new_status = self.pole_sim.toggle_pole_status(pole_id)
            return new_status
        elif action in ['on', 'off']:
            success = self.pole_sim.set_pole_status(pole_id, action)
            return action if success else None
        else:
            print(f"Invalid action: {action}. Use 'on', 'off', or 'toggle'")
            return None
    
    def list_poles(self):
        """List all smart poles with their status"""
        query = """
            SELECT sp.pole_id, sp.location, sp.status, 
                   COUNT(spm.id) as module_count
            FROM smart_poles sp
            LEFT JOIN smart_pole_modules spm ON sp.pole_id = spm.pole_id
            GROUP BY sp.pole_id, sp.location, sp.status
            ORDER BY sp.pole_id
        """
        
        poles = self.db.fetch_all(query)
        
        print(f"\n{'='*70}")
        print(f"{'Pole ID':<10} {'Location':<25} {'Status':<10} {'Modules':<10}")
        print(f"{'='*70}")
        
        for pole in poles:
            pole_id, location, status, module_count = pole
            print(f"{pole_id:<10} {location:<25} {status.upper():<10} {module_count:<10}")
        
        print(f"{'='*70}\n")
    
    def view_latest_data(self):
        """View latest data from all systems"""
        # Latest weather data
        weather_query = """
            SELECT temperature_c, humidity_percent, pressure_hpa, 
                   wind_speed_ms, rainfall_mm, light_intensity_lux, timestamp
            FROM weather_station
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        weather = self.db.fetch_one(weather_query)
        
        if weather:
            print(f"\n{'='*70}")
            print("Latest Weather Data")
            print(f"{'='*70}")
            print(f"Temperature: {weather[0]}°C")
            print(f"Humidity: {weather[1]}%")
            print(f"Pressure: {weather[2]} hPa")
            print(f"Wind Speed: {weather[3]} m/s")
            print(f"Rainfall: {weather[4]} mm")
            print(f"Light Intensity: {weather[5]} lux")
            print(f"Timestamp: {weather[6]}")
        
        # Latest energy data for each pole
        energy_query = """
            SELECT DISTINCT ON (pole_id) 
                pole_id, power_consumption_w, voltage_v, 
                current_a, energy_kwh, status, timestamp
            FROM smart_pole_energy
            ORDER BY pole_id, timestamp DESC
        """
        
        energy_data = self.db.fetch_all(energy_query)
        
        if energy_data:
            print(f"\n{'='*70}")
            print("Latest Smart Pole Energy Data")
            print(f"{'='*70}")
            print(f"{'Pole ID':<10} {'Status':<8} {'Power (W)':<12} {'Energy (kWh)':<15}")
            print(f"{'-'*70}")
            
            for data in energy_data:
                pole_id, power, voltage, current, energy, status, timestamp = data
                print(f"{pole_id:<10} {status.upper():<8} {power:<12.2f} {energy:<15.4f}")
        
        # Latest power meter readings
        power_meter_query = """
            SELECT DISTINCT ON (pmr.meter_id)
                pmr.meter_id, pm.meter_type, pmr.power_w, pmr.energy_kwh, pmr.timestamp
            FROM power_meter_readings pmr
            JOIN power_meters pm ON pmr.meter_id = pm.meter_id
            ORDER BY pmr.meter_id, pmr.timestamp DESC
        """
        
        power_meter_data = self.db.fetch_all(power_meter_query)
        
        if power_meter_data:
            print(f"\n{'='*70}")
            print("Latest Power Meter Readings")
            print(f"{'='*70}")
            print(f"{'Meter ID':<12} {'Type':<10} {'Power (W)':<12} {'Energy (kWh)':<15}")
            print(f"{'-'*70}")
            
            for data in power_meter_data:
                meter_id, meter_type, power, energy, timestamp = data
                print(f"{meter_id:<12} {meter_type:<10} {power:<12.2f} {energy:<15.4f}")
        
        # Latest flow meter readings
        flow_meter_query = """
            SELECT DISTINCT ON (fmr.meter_id)
                fmr.meter_id, fm.meter_type, fm.flow_unit, fmr.flow_rate, 
                fmr.total_volume, fmr.timestamp
            FROM flow_meter_readings fmr
            JOIN flow_meters fm ON fmr.meter_id = fm.meter_id
            ORDER BY fmr.meter_id, fmr.timestamp DESC
        """
        
        flow_meter_data = self.db.fetch_all(flow_meter_query)
        
        if flow_meter_data:
            print(f"\n{'='*70}")
            print("Latest Flow Meter Readings")
            print(f"{'='*70}")
            print(f"{'Meter ID':<12} {'Type':<8} {'Flow Rate':<20} {'Total Volume':<15}")
            print(f"{'-'*70}")
            
            for data in flow_meter_data:
                meter_id, meter_type, flow_unit, flow_rate, total_volume, timestamp = data
                print(f"{meter_id:<12} {meter_type:<8} {flow_rate:<8.3f} {flow_unit:<11} {total_volume:<15.3f}")
        
        print(f"{'='*70}\n")
    
    def list_power_meters(self):
        """List all power meters"""
        query = """
            SELECT meter_id, meter_type, location, room_name, building, status
            FROM power_meters
            ORDER BY meter_type, meter_id
        """
        
        meters = self.db.fetch_all(query)
        
        print(f"\n{'='*80}")
        print(f"{'Meter ID':<12} {'Type':<10} {'Room/Location':<25} {'Building':<15} {'Status':<10}")
        print(f"{'='*80}")
        
        for meter in meters:
            meter_id, meter_type, location, room_name, building, status = meter
            room_display = room_name if room_name else location[:24]
            building_display = building if building else '-'
            print(f"{meter_id:<12} {meter_type:<10} {room_display:<25} {building_display:<15} {status.upper():<10}")
        
        print(f"{'='*80}\n")
    
    def list_flow_meters(self):
        """List all flow meters"""
        query = """
            SELECT meter_id, meter_type, flow_unit, location, building, status
            FROM flow_meters
            ORDER BY meter_type, meter_id
        """
        
        meters = self.db.fetch_all(query)
        
        print(f"\n{'='*80}")
        print(f"{'Meter ID':<12} {'Type':<8} {'Unit':<12} {'Location':<25} {'Building':<15}")
        print(f"{'='*80}")
        
        for meter in meters:
            meter_id, meter_type, flow_unit, location, building, status = meter
            building_display = building if building else '-'
            print(f"{meter_id:<12} {meter_type:<8} {flow_unit:<12} {location[:24]:<25} {building_display:<15}")
        
        print(f"{'='*80}\n")
    
    def list_categories(self):
        """List all device categories"""
        query = """
            SELECT category_id, category_name, description
            FROM device_categories
            ORDER BY category_name
        """
        
        categories = self.db.fetch_all(query)
        
        print(f"\n{'='*80}")
        print("Device Categories")
        print(f"{'='*80}")
        print(f"{'Category ID':<20} {'Name':<30} {'Description':<30}")
        print(f"{'-'*80}")
        
        for cat in categories:
            cat_id, name, desc = cat
            desc_display = (desc[:27] + '...') if desc and len(desc) > 30 else (desc if desc else '')
            print(f"{cat_id:<20} {name:<30} {desc_display:<30}")
        
        print(f"{'='*80}\n")
    
    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...")
        self.db.disconnect()
        print("Goodbye!")

def print_usage():
    """Print usage information"""
    print("""
Smart City Data Generator
==========================

Usage:
    python main.py [command] [options]

Commands:
    generate          Generate single cycle of data for all devices
    continuous        Run continuous data generation (default: 60s interval)
    list              List all smart poles and their status
    list-power        List all power meters (1-phase and 3-phase)
    list-flow         List all flow meters (water, gas, steam, air)
    list-categories   List all device categories
    control           Control a smart pole (on/off/toggle)
    view              View latest data from all systems
    api               Start REST API server (Swagger UI at http://localhost:8000/docs)
    help              Show this help message

Examples:
    python main.py generate
    python main.py continuous
    python main.py continuous 30        # 30-second interval
    python main.py list
    python main.py list-power
    python main.py list-flow
    python main.py list-categories
    python main.py control SP001 on
    python main.py control SP002 off
    python main.py control SP003 toggle
    python main.py view
    python main.py api                  # Start REST API with Swagger
    """)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        command = 'continuous'
    else:
        command = sys.argv[1]
    
    if command == 'help':
        print_usage()
        return
    
    # API command doesn't need generator
    if command == 'api':
        print("Starting REST API server...")
        print("Swagger UI available at: http://localhost:8000/docs")
        print("ReDoc available at: http://localhost:8000/redoc")
        print("Press Ctrl+C to stop\n")
        import uvicorn
        from api import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return
    
    generator = SmartCityDataGenerator()
    
    if not generator.initialize():
        print("\nFailed to initialize. Please check:")
        print("1. PostgreSQL is running (docker compose up -d)")
        print("2. Database connection settings in .env file")
        sys.exit(1)
    
    if command == 'generate':
        generator.run_single()
    
    elif command == 'continuous':
        interval = 60
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                print(f"Invalid interval: {sys.argv[2]}. Using default (60s)")
        generator.run_continuous(interval)
    
    elif command == 'list':
        generator.list_poles()
        generator.cleanup()
    
    elif command == 'list-power':
        generator.list_power_meters()
        generator.cleanup()
    
    elif command == 'list-flow':
        generator.list_flow_meters()
        generator.cleanup()
    
    elif command == 'list-categories':
        generator.list_categories()
        generator.cleanup()
    
    elif command == 'control':
        if len(sys.argv) < 4:
            print("Usage: python main.py control <pole_id> <on|off|toggle>")
            print("Example: python main.py control SP001 on")
        else:
            pole_id = sys.argv[2]
            action = sys.argv[3].lower()
            generator.control_pole(pole_id, action)
        generator.cleanup()
    
    elif command == 'view':
        generator.view_latest_data()
        generator.cleanup()
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        generator.cleanup()

if __name__ == "__main__":
    main()
