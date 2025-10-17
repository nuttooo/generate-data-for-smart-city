import random
from datetime import datetime
import math

class PowerMeterSimulator:
    """Simulate realistic power meter readings for 1-phase and 3-phase meters"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        # Typical power consumption patterns for different room types
        self.room_patterns = {
            'office': {'base': 500, 'peak': 1500, 'variation': 0.2},
            'room': {'base': 200, 'peak': 800, 'variation': 0.25},
            'main_panel': {'base': 5000, 'peak': 15000, 'variation': 0.15}
        }
    
    def get_meter_info(self, meter_id):
        """Get meter information"""
        query = "SELECT meter_type, room_name, status FROM power_meters WHERE meter_id = %s"
        result = self.db.fetch_one(query, (meter_id,))
        if result:
            return {
                'meter_type': result[0],
                'room_name': result[1],
                'status': result[2]
            }
        return None
    
    def get_all_meters(self):
        """Get all power meter IDs"""
        query = "SELECT meter_id FROM power_meters WHERE status = 'active'"
        results = self.db.fetch_all(query)
        return [row[0] for row in results]
    
    def get_time_factor(self):
        """Get time-based factor for power consumption"""
        hour = datetime.now().hour
        
        # Business hours pattern (8 AM - 6 PM)
        if 8 <= hour < 18:
            # Peak hours (9 AM - 5 PM)
            if 9 <= hour < 17:
                return 1.0  # Peak consumption
            else:
                return 0.7  # Start/end of business hours
        elif 6 <= hour < 8:
            return 0.4  # Early morning
        elif 18 <= hour < 22:
            return 0.6  # Evening
        else:
            return 0.2  # Night time
    
    def determine_room_type(self, room_name):
        """Determine room type from name"""
        if not room_name:
            return 'main_panel'
        
        room_lower = room_name.lower()
        if 'office' in room_lower:
            return 'office'
        elif 'panel' in room_lower or 'main' in room_lower:
            return 'main_panel'
        else:
            return 'room'
    
    def generate_1phase_reading(self, meter_id, meter_info):
        """Generate 1-phase power meter reading"""
        room_type = self.determine_room_type(meter_info['room_name'])
        pattern = self.room_patterns[room_type]
        
        time_factor = self.get_time_factor()
        
        # Calculate power consumption
        base_power = pattern['base'] + (pattern['peak'] - pattern['base']) * time_factor
        variation = random.uniform(1 - pattern['variation'], 1 + pattern['variation'])
        power_w = base_power * variation
        
        # Electrical parameters for 1-phase (230V Thailand)
        voltage_v = random.uniform(220, 240)
        power_factor = random.uniform(0.85, 0.95)
        current_a = power_w / (voltage_v * power_factor)
        frequency_hz = random.uniform(49.9, 50.1)
        
        # Energy (kWh for 1 hour interval)
        energy_kwh = power_w / 1000.0
        
        return {
            'voltage_v': round(voltage_v, 2),
            'current_a': round(current_a, 4),
            'power_w': round(power_w, 2),
            'power_factor': round(power_factor, 3),
            'energy_kwh': round(energy_kwh, 4),
            'frequency_hz': round(frequency_hz, 2),
            'voltage_l1_v': None,
            'voltage_l2_v': None,
            'voltage_l3_v': None,
            'current_l1_a': None,
            'current_l2_a': None,
            'current_l3_a': None,
            'power_l1_w': None,
            'power_l2_w': None,
            'power_l3_w': None
        }
    
    def generate_3phase_reading(self, meter_id, meter_info):
        """Generate 3-phase power meter reading"""
        room_type = self.determine_room_type(meter_info['room_name'])
        pattern = self.room_patterns[room_type]
        
        time_factor = self.get_time_factor()
        
        # Calculate total power consumption
        base_power = pattern['base'] + (pattern['peak'] - pattern['base']) * time_factor
        variation = random.uniform(1 - pattern['variation'], 1 + pattern['variation'])
        total_power_w = base_power * variation
        
        # Distribute power across three phases (slightly unbalanced)
        phase_distribution = [
            random.uniform(0.30, 0.35),
            random.uniform(0.30, 0.35),
            random.uniform(0.30, 0.35)
        ]
        # Normalize to ensure sum equals 1
        total = sum(phase_distribution)
        phase_distribution = [p / total for p in phase_distribution]
        
        power_l1_w = total_power_w * phase_distribution[0]
        power_l2_w = total_power_w * phase_distribution[1]
        power_l3_w = total_power_w * phase_distribution[2]
        
        # Electrical parameters for 3-phase (400V line-to-line, 230V line-to-neutral)
        voltage_l1_v = random.uniform(220, 240)
        voltage_l2_v = random.uniform(220, 240)
        voltage_l3_v = random.uniform(220, 240)
        
        power_factor = random.uniform(0.85, 0.95)
        
        current_l1_a = power_l1_w / (voltage_l1_v * power_factor)
        current_l2_a = power_l2_w / (voltage_l2_v * power_factor)
        current_l3_a = power_l3_w / (voltage_l3_v * power_factor)
        
        # Average values
        voltage_v = (voltage_l1_v + voltage_l2_v + voltage_l3_v) / 3
        current_a = (current_l1_a + current_l2_a + current_l3_a)
        frequency_hz = random.uniform(49.9, 50.1)
        
        # Energy (kWh for 1 hour interval)
        energy_kwh = total_power_w / 1000.0
        
        return {
            'voltage_v': round(voltage_v, 2),
            'current_a': round(current_a, 4),
            'power_w': round(total_power_w, 2),
            'power_factor': round(power_factor, 3),
            'energy_kwh': round(energy_kwh, 4),
            'frequency_hz': round(frequency_hz, 2),
            'voltage_l1_v': round(voltage_l1_v, 2),
            'voltage_l2_v': round(voltage_l2_v, 2),
            'voltage_l3_v': round(voltage_l3_v, 2),
            'current_l1_a': round(current_l1_a, 4),
            'current_l2_a': round(current_l2_a, 4),
            'current_l3_a': round(current_l3_a, 4),
            'power_l1_w': round(power_l1_w, 2),
            'power_l2_w': round(power_l2_w, 2),
            'power_l3_w': round(power_l3_w, 2)
        }
    
    def generate_reading(self, meter_id):
        """Generate power meter reading based on meter type"""
        meter_info = self.get_meter_info(meter_id)
        
        if not meter_info or meter_info['status'] != 'active':
            return None
        
        if meter_info['meter_type'] == '1-phase':
            return self.generate_1phase_reading(meter_id, meter_info)
        elif meter_info['meter_type'] == '3-phase':
            return self.generate_3phase_reading(meter_id, meter_info)
        
        return None
