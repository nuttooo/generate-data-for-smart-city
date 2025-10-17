import random
from datetime import datetime

class SmartPoleSimulator:
    """Simulate realistic smart pole energy consumption"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.module_variations = {
            'lighting': 0.15,  # ±15% variation
            'camera': 0.10,    # ±10% variation
            'sensor': 0.05,    # ±5% variation
            'wifi': 0.12,      # ±12% variation
            'display': 0.20,   # ±20% variation
            'charging': 0.30   # ±30% variation (highly variable)
        }
    
    def get_pole_status(self, pole_id):
        """Get current status of a smart pole"""
        query = "SELECT status FROM smart_poles WHERE pole_id = %s"
        result = self.db.fetch_one(query, (pole_id,))
        return result[0] if result else 'off'
    
    def get_pole_modules(self, pole_id):
        """Get all modules for a specific pole"""
        query = """
            SELECT module_type, module_name, power_rating_w, status
            FROM smart_pole_modules
            WHERE pole_id = %s AND status = 'active'
        """
        modules = self.db.fetch_all(query, (pole_id,))
        return modules
    
    def calculate_module_power(self, module_type, base_power, light_intensity):
        """Calculate actual power consumption for a module based on conditions"""
        hour = datetime.now().hour
        
        # Lighting adjustment based on ambient light
        if module_type == 'lighting':
            if 6 <= hour < 18:  # Daytime
                # Reduce power based on light intensity
                if light_intensity > 50000:
                    power_factor = 0.1  # 10% power during bright daylight
                elif light_intensity > 20000:
                    power_factor = 0.3  # 30% power during cloudy day
                else:
                    power_factor = 0.7  # 70% power during overcast
            else:  # Nighttime
                power_factor = 1.0  # Full power at night
        
        # Display adjustment based on time of day
        elif module_type == 'display':
            if 6 <= hour < 22:
                power_factor = 1.0  # Full power during active hours
            else:
                power_factor = 0.3  # Reduced power at night
        
        # Charging station - highly variable based on usage
        elif module_type == 'charging':
            # Random usage pattern (0-100% utilization)
            power_factor = random.uniform(0.0, 1.0)
        
        # Other modules have consistent power draw
        else:
            power_factor = 1.0
        
        # Apply module-specific variation
        variation = self.module_variations.get(module_type, 0.05)
        random_factor = random.uniform(1 - variation, 1 + variation)
        
        actual_power = base_power * power_factor * random_factor
        return actual_power
    
    def generate_energy_data(self, pole_id, weather_data):
        """Generate energy consumption data for a smart pole"""
        status = self.get_pole_status(pole_id)
        
        # If pole is off, return minimal standby power
        if status == 'off':
            return {
                'power_consumption_w': 2.0,  # Standby power
                'voltage_v': 230.0,
                'current_a': 0.009,
                'energy_kwh': 0.002,
                'status': 'off'
            }
        
        # Get all modules and calculate total power
        modules = self.get_pole_modules(pole_id)
        total_power = 0.0
        
        light_intensity = weather_data.get('light_intensity_lux', 50000)
        
        for module in modules:
            module_type, module_name, power_rating, module_status = module
            module_power = self.calculate_module_power(
                module_type, 
                float(power_rating), 
                light_intensity
            )
            total_power += module_power
        
        # Add base system power (control unit, etc.)
        base_system_power = 10.0
        total_power += base_system_power
        
        # Calculate electrical parameters
        voltage = random.uniform(220.0, 240.0)  # Grid voltage variation
        current = total_power / voltage
        
        # Energy in kWh (for 1-hour interval, energy = power)
        energy_kwh = total_power / 1000.0
        
        return {
            'power_consumption_w': round(total_power, 2),
            'voltage_v': round(voltage, 2),
            'current_a': round(current, 4),
            'energy_kwh': round(energy_kwh, 4),
            'status': 'on'
        }
    
    def get_all_poles(self):
        """Get all smart pole IDs"""
        query = "SELECT pole_id FROM smart_poles"
        results = self.db.fetch_all(query)
        return [row[0] for row in results]
    
    def toggle_pole_status(self, pole_id):
        """Toggle smart pole on/off"""
        current_status = self.get_pole_status(pole_id)
        new_status = 'off' if current_status == 'on' else 'on'
        
        query = """
            UPDATE smart_poles 
            SET status = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE pole_id = %s
        """
        success = self.db.execute_query(query, (new_status, pole_id))
        
        if success:
            print(f"Smart pole {pole_id} status changed: {current_status} -> {new_status}")
            return new_status
        return None
    
    def set_pole_status(self, pole_id, status):
        """Set smart pole to specific status (on/off)"""
        if status not in ['on', 'off']:
            print(f"Invalid status: {status}. Must be 'on' or 'off'")
            return False
        
        query = """
            UPDATE smart_poles 
            SET status = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE pole_id = %s
        """
        success = self.db.execute_query(query, (status, pole_id))
        
        if success:
            print(f"Smart pole {pole_id} status set to: {status}")
            return True
        return False
