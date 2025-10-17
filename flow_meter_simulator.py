import random
from datetime import datetime
import math

class FlowMeterSimulator:
    """Simulate realistic flow meter readings for various fluid types"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
        # Flow patterns for different meter types and times
        self.flow_patterns = {
            'water': {
                'base_flow': 10.0,      # L/min
                'peak_flow': 50.0,      # L/min
                'variation': 0.3,
                'night_factor': 0.1
            },
            'gas': {
                'base_flow': 2.0,       # m3/h
                'peak_flow': 15.0,      # m3/h
                'variation': 0.35,
                'night_factor': 0.05
            },
            'steam': {
                'base_flow': 50.0,      # kg/h
                'peak_flow': 400.0,     # kg/h
                'variation': 0.25,
                'night_factor': 0.2
            },
            'air': {
                'base_flow': 2.0,       # m3/min
                'peak_flow': 20.0,      # m3/min
                'variation': 0.4,
                'night_factor': 0.1
            }
        }
        
        # Running totals (in-memory, would be better to store in DB)
        self.total_volumes = {}
    
    def get_meter_info(self, meter_id):
        """Get flow meter information"""
        query = """
            SELECT meter_type, flow_unit, location, max_flow_rate, status 
            FROM flow_meters 
            WHERE meter_id = %s
        """
        result = self.db.fetch_one(query, (meter_id,))
        if result:
            return {
                'meter_type': result[0],
                'flow_unit': result[1],
                'location': result[2],
                'max_flow_rate': float(result[3]) if result[3] else None,
                'status': result[4]
            }
        return None
    
    def get_all_meters(self):
        """Get all flow meter IDs"""
        query = "SELECT meter_id FROM flow_meters WHERE status = 'active'"
        results = self.db.fetch_all(query)
        return [row[0] for row in results]
    
    def get_time_factor(self, meter_type):
        """Get time-based factor for flow rate"""
        hour = datetime.now().hour
        
        if meter_type == 'water':
            # Water usage peaks in morning (6-9) and evening (17-21)
            if 6 <= hour < 9 or 17 <= hour < 21:
                return 1.0
            elif 9 <= hour < 17:
                return 0.6
            else:
                return 0.1  # Night time
        
        elif meter_type == 'gas':
            # Gas usage peaks during meal times
            if 6 <= hour < 9 or 11 <= hour < 14 or 17 <= hour < 21:
                return 1.0
            elif 9 <= hour < 11 or 14 <= hour < 17:
                return 0.4
            else:
                return 0.05  # Night time
        
        elif meter_type == 'steam':
            # Industrial steam usage during business hours
            if 8 <= hour < 17:
                return 1.0
            elif 6 <= hour < 8 or 17 <= hour < 20:
                return 0.5
            else:
                return 0.2  # Night time
        
        elif meter_type == 'air':
            # Compressed air usage during production hours
            if 8 <= hour < 17:
                return 1.0
            elif 6 <= hour < 8 or 17 <= hour < 20:
                return 0.4
            else:
                return 0.1  # Night time
        
        return 0.5  # Default
    
    def get_last_total_volume(self, meter_id):
        """Get last recorded total volume from database"""
        query = """
            SELECT total_volume 
            FROM flow_meter_readings 
            WHERE meter_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        result = self.db.fetch_one(query, (meter_id,))
        if result:
            return float(result[0])
        return 0.0
    
    def generate_water_reading(self, meter_id, meter_info):
        """Generate water flow meter reading"""
        pattern = self.flow_patterns['water']
        time_factor = self.get_time_factor('water')
        
        # Calculate flow rate
        base_flow = pattern['base_flow'] + (pattern['peak_flow'] - pattern['base_flow']) * time_factor
        variation = random.uniform(1 - pattern['variation'], 1 + pattern['variation'])
        flow_rate = base_flow * variation
        
        # Ensure within meter's max capacity
        if meter_info['max_flow_rate']:
            flow_rate = min(flow_rate, meter_info['max_flow_rate'])
        
        # Calculate total volume (accumulate over time)
        # Assuming readings every minute, convert L/min to total L
        if meter_id not in self.total_volumes:
            self.total_volumes[meter_id] = self.get_last_total_volume(meter_id)
        
        # Add flow for 1 minute interval
        volume_increment = flow_rate * 1.0  # 1 minute
        self.total_volumes[meter_id] += volume_increment
        
        # Water properties
        temperature_c = random.uniform(15, 30)
        pressure_bar = random.uniform(2.0, 4.0)
        
        return {
            'flow_rate': round(flow_rate, 3),
            'total_volume': round(self.total_volumes[meter_id], 3),
            'temperature_c': round(temperature_c, 2),
            'pressure_bar': round(pressure_bar, 2),
            'density': None  # Not applicable for volumetric water meters
        }
    
    def generate_gas_reading(self, meter_id, meter_info):
        """Generate gas flow meter reading"""
        pattern = self.flow_patterns['gas']
        time_factor = self.get_time_factor('gas')
        
        # Calculate flow rate
        base_flow = pattern['base_flow'] + (pattern['peak_flow'] - pattern['base_flow']) * time_factor
        variation = random.uniform(1 - pattern['variation'], 1 + pattern['variation'])
        flow_rate = base_flow * variation
        
        if meter_info['max_flow_rate']:
            flow_rate = min(flow_rate, meter_info['max_flow_rate'])
        
        # Calculate total volume (m3/h to m3, for 1 minute = 1/60 hour)
        if meter_id not in self.total_volumes:
            self.total_volumes[meter_id] = self.get_last_total_volume(meter_id)
        
        volume_increment = flow_rate / 60.0  # Convert m3/h to m3/min
        self.total_volumes[meter_id] += volume_increment
        
        # Gas properties
        temperature_c = random.uniform(20, 25)
        pressure_bar = random.uniform(0.5, 2.0)
        
        return {
            'flow_rate': round(flow_rate, 3),
            'total_volume': round(self.total_volumes[meter_id], 3),
            'temperature_c': round(temperature_c, 2),
            'pressure_bar': round(pressure_bar, 2),
            'density': None
        }
    
    def generate_steam_reading(self, meter_id, meter_info):
        """Generate steam flow meter reading (mass flow)"""
        pattern = self.flow_patterns['steam']
        time_factor = self.get_time_factor('steam')
        
        # Calculate flow rate (kg/h)
        base_flow = pattern['base_flow'] + (pattern['peak_flow'] - pattern['base_flow']) * time_factor
        variation = random.uniform(1 - pattern['variation'], 1 + pattern['variation'])
        flow_rate = base_flow * variation
        
        if meter_info['max_flow_rate']:
            flow_rate = min(flow_rate, meter_info['max_flow_rate'])
        
        # Calculate total mass (kg/h to kg, for 1 minute = 1/60 hour)
        if meter_id not in self.total_volumes:
            self.total_volumes[meter_id] = self.get_last_total_volume(meter_id)
        
        mass_increment = flow_rate / 60.0
        self.total_volumes[meter_id] += mass_increment
        
        # Steam properties
        temperature_c = random.uniform(150, 180)  # Saturated steam
        pressure_bar = random.uniform(5.0, 10.0)
        density = random.uniform(3.0, 5.0)  # kg/m3 at steam conditions
        
        return {
            'flow_rate': round(flow_rate, 3),
            'total_volume': round(self.total_volumes[meter_id], 3),  # Actually total mass
            'temperature_c': round(temperature_c, 2),
            'pressure_bar': round(pressure_bar, 2),
            'density': round(density, 3)
        }
    
    def generate_air_reading(self, meter_id, meter_info):
        """Generate compressed air flow meter reading"""
        pattern = self.flow_patterns['air']
        time_factor = self.get_time_factor('air')
        
        # Calculate flow rate (m3/min)
        base_flow = pattern['base_flow'] + (pattern['peak_flow'] - pattern['base_flow']) * time_factor
        variation = random.uniform(1 - pattern['variation'], 1 + pattern['variation'])
        flow_rate = base_flow * variation
        
        if meter_info['max_flow_rate']:
            flow_rate = min(flow_rate, meter_info['max_flow_rate'])
        
        # Calculate total volume
        if meter_id not in self.total_volumes:
            self.total_volumes[meter_id] = self.get_last_total_volume(meter_id)
        
        volume_increment = flow_rate * 1.0  # 1 minute
        self.total_volumes[meter_id] += volume_increment
        
        # Compressed air properties
        temperature_c = random.uniform(25, 40)
        pressure_bar = random.uniform(6.0, 8.0)  # Typical compressed air pressure
        
        return {
            'flow_rate': round(flow_rate, 3),
            'total_volume': round(self.total_volumes[meter_id], 3),
            'temperature_c': round(temperature_c, 2),
            'pressure_bar': round(pressure_bar, 2),
            'density': None
        }
    
    def generate_reading(self, meter_id):
        """Generate flow meter reading based on meter type"""
        meter_info = self.get_meter_info(meter_id)
        
        if not meter_info or meter_info['status'] != 'active':
            return None
        
        meter_type = meter_info['meter_type']
        
        if meter_type == 'water':
            return self.generate_water_reading(meter_id, meter_info)
        elif meter_type == 'gas':
            return self.generate_gas_reading(meter_id, meter_info)
        elif meter_type == 'steam':
            return self.generate_steam_reading(meter_id, meter_info)
        elif meter_type == 'air':
            return self.generate_air_reading(meter_id, meter_info)
        
        return None
