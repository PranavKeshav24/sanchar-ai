"""
Advanced Traffic Prediction & V2I Communication System
Implements ML-based traffic density prediction and V2V/V2I communication
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import random


class AdvancedTrafficPredictor:
    """
    ML-based traffic density prediction using time series and spatial analysis
    Predicts traffic patterns based on historical data, time, location, and weather
    """
    
    def __init__(self):
        # Simulated trained model weights
        self.time_weights = self._initialize_time_weights()
        self.location_weights = self._initialize_location_weights()
        self.weather_weights = {
            'clear': 1.0,
            'rain': 1.3,
            'snow': 1.5,
            'fog': 1.2
        }
        
        # Historical traffic patterns (simulated)
        self.historical_data = self._load_historical_patterns()
    
    def _initialize_time_weights(self) -> Dict[int, float]:
        """Initialize time-of-day traffic multipliers"""
        return {
            0: 0.2, 1: 0.15, 2: 0.1, 3: 0.1, 4: 0.15, 5: 0.4,   # Night/Early morning
            6: 0.7, 7: 0.9, 8: 1.0, 9: 0.85, 10: 0.7, 11: 0.75, # Morning rush
            12: 0.8, 13: 0.75, 14: 0.7, 15: 0.75, 16: 0.85,     # Afternoon
            17: 1.0, 18: 0.95, 19: 0.8, 20: 0.6, 21: 0.5,       # Evening rush
            22: 0.4, 23: 0.3                                     # Night
        }
    
    def _initialize_location_weights(self) -> Dict[str, float]:
        """Initialize location type traffic multipliers"""
        return {
            'urban_center': 1.5,
            'residential': 0.8,
            'highway': 1.2,
            'industrial': 1.0,
            'rural': 0.4
        }
    
    def _load_historical_patterns(self) -> Dict:
        """Load simulated historical traffic patterns"""
        return {
            'weekday_pattern': [0.3, 0.2, 0.15, 0.15, 0.3, 0.6, 0.85, 1.0, 0.8, 0.7, 0.7, 0.75,
                               0.8, 0.75, 0.7, 0.75, 0.9, 1.0, 0.9, 0.7, 0.5, 0.4, 0.35, 0.3],
            'weekend_pattern': [0.2, 0.15, 0.1, 0.1, 0.15, 0.25, 0.4, 0.55, 0.65, 0.7, 0.75, 0.8,
                               0.85, 0.8, 0.75, 0.75, 0.7, 0.7, 0.65, 0.6, 0.5, 0.4, 0.3, 0.25]
        }
    
    def predict_traffic_density(
        self,
        lat: float,
        lng: float,
        time_of_day: int,
        day_of_week: int,
        weather_conditions: Optional[Dict] = None
    ) -> Dict:
        """
        Predict traffic density for a location at a specific time
        
        Returns:
            {
                'density': float (0-100),
                'confidence': float (0-1),
                'predicted_speed': float (km/h),
                'congestion_level': str,
                'prediction_factors': dict
            }
        """
        # Get base pattern from historical data
        is_weekend = day_of_week >= 5
        pattern = self.historical_data['weekend_pattern'] if is_weekend else self.historical_data['weekday_pattern']
        base_density = pattern[time_of_day % 24]
        
        # Apply time weight
        time_multiplier = self.time_weights.get(time_of_day, 0.5)
        
        # Estimate location type based on coordinates
        location_type = self._estimate_location_type(lat, lng)
        location_multiplier = self.location_weights.get(location_type, 1.0)
        
        # Apply weather impact
        weather_multiplier = 1.0
        if weather_conditions:
            temp = weather_conditions.get('temperature', 25)
            humidity = weather_conditions.get('humidity', 50)
            visibility = weather_conditions.get('visibility', 10)
            
            # Adjust for weather
            if visibility < 5:
                weather_multiplier *= 1.2
            if temp < 0:
                weather_multiplier *= 1.3
            if humidity > 80:
                weather_multiplier *= 1.1
        
        # Calculate final density (0-100 scale)
        predicted_density = min(
            base_density * time_multiplier * location_multiplier * weather_multiplier * 100,
            100
        )
        
        # Calculate predicted speed based on density
        max_speed = 60 if location_type == 'urban_center' else 80
        predicted_speed = max_speed * (1 - (predicted_density / 150))
        predicted_speed = max(10, min(predicted_speed, max_speed))
        
        # Determine congestion level
        congestion_level = self._classify_congestion(predicted_density)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(
            has_weather=weather_conditions is not None,
            time_reliability=0.9,
            location_precision=0.85
        )
        
        # Predict next hour trend
        next_hour_density = pattern[(time_of_day + 1) % 24] * time_multiplier * location_multiplier * 100
        trend = 'increasing' if next_hour_density > predicted_density else 'decreasing' if next_hour_density < predicted_density else 'stable'
        
        return {
            'density': round(predicted_density, 2),
            'confidence': round(confidence, 2),
            'predicted_speed': round(predicted_speed, 2),
            'congestion_level': congestion_level,
            'trend': trend,
            'prediction_factors': {
                'time_multiplier': round(time_multiplier, 2),
                'location_type': location_type,
                'location_multiplier': round(location_multiplier, 2),
                'weather_multiplier': round(weather_multiplier, 2),
                'is_weekend': is_weekend
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_traffic_pattern(
        self,
        lat: float,
        lng: float,
        hours_ahead: int = 24,
        weather_forecast: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Predict traffic pattern for the next N hours
        """
        current_time = datetime.now()
        predictions = []
        
        for hour_offset in range(hours_ahead):
            future_time = current_time + timedelta(hours=hour_offset)
            time_of_day = future_time.hour
            day_of_week = future_time.weekday()
            
            weather = None
            if weather_forecast and hour_offset < len(weather_forecast):
                weather = weather_forecast[hour_offset]
            
            prediction = self.predict_traffic_density(
                lat, lng, time_of_day, day_of_week, weather
            )
            prediction['timestamp'] = future_time.isoformat()
            predictions.append(prediction)
        
        return predictions
    
    def _estimate_location_type(self, lat: float, lng: float) -> str:
        """Estimate location type based on coordinates"""
        # Simple heuristic - in production, use actual location data
        lat_abs = abs(lat)
        lng_abs = abs(lng)
        
        # Urban centers tend to be at specific coordinates
        if lat_abs > 10 and lat_abs < 60:  # Mid-latitude cities
            return 'urban_center'
        elif lat_abs < 10:
            return 'rural'
        else:
            return 'residential'
    
    def _classify_congestion(self, density: float) -> str:
        """Classify traffic congestion level"""
        if density < 20:
            return 'free_flow'
        elif density < 40:
            return 'light'
        elif density < 60:
            return 'moderate'
        elif density < 80:
            return 'heavy'
        else:
            return 'severe'
    
    def _calculate_confidence(
        self,
        has_weather: bool,
        time_reliability: float,
        location_precision: float
    ) -> float:
        """Calculate prediction confidence score"""
        base_confidence = 0.7
        
        if has_weather:
            base_confidence += 0.1
        
        confidence = base_confidence * time_reliability * location_precision
        return min(confidence, 0.99)


class V2ICommunicationSystem:
    """
    Vehicle-to-Infrastructure (V2I) Communication System
    Manages V2V, V2I, and V2X communication for intelligent traffic management
    """
    
    def __init__(self):
        self.registered_vehicles = {}
        self.infrastructure_nodes = {}
        self.active_signals = {}
        self.communication_log = []
        
        # Communication parameters
        self.v2i_range = 500  # meters
        self.v2v_range = 300  # meters
        self.latency_threshold = 10  # ms for URLLC
    
    def register_vehicle(
        self,
        vehicle_id: str,
        vehicle_type: str,
        location: Dict[str, float]
    ) -> Dict:
        """
        Register vehicle in V2I system
        
        Args:
            vehicle_id: Unique vehicle identifier
            vehicle_type: Type (car, ambulance, bus, etc.)
            location: {'lat': float, 'lng': float}
        """
        priority_level = self._determine_priority(vehicle_type)
        
        vehicle_info = {
            'vehicle_id': vehicle_id,
            'vehicle_type': vehicle_type,
            'location': location,
            'priority_level': priority_level,
            'communication_mode': self._assign_communication_mode(vehicle_type),
            'slice_type': self._assign_network_slice(vehicle_type),
            'bandwidth': self._allocate_bandwidth(vehicle_type),
            'registered_at': datetime.now().isoformat(),
            'status': 'active',
            'signal_strength': random.randint(-70, -50),  # dBm
            'latency': random.randint(5, 15) if vehicle_type == 'ambulance' else random.randint(10, 50)
        }
        
        self.registered_vehicles[vehicle_id] = vehicle_info
        self._log_communication('vehicle_registration', vehicle_id, 'Vehicle registered successfully')
        
        return vehicle_info
    
    def request_priority_signal(
        self,
        vehicle_id: str,
        destination: Dict[str, float]
    ) -> Dict:
        """
        Request traffic signal priority (for emergency vehicles)
        """
        if vehicle_id not in self.registered_vehicles:
            return {'error': 'Vehicle not registered'}
        
        vehicle = self.registered_vehicles[vehicle_id]
        
        if vehicle['priority_level'] < 8:  # Only high-priority vehicles
            return {'error': 'Vehicle does not have priority clearance'}
        
        # Calculate route and affected intersections
        route_intersections = self._identify_route_intersections(
            vehicle['location'],
            destination
        )
        
        # Grant priority at each intersection
        priority_grants = []
        for intersection in route_intersections:
            grant = self._grant_signal_priority(vehicle_id, intersection)
            priority_grants.append(grant)
        
        self._log_communication(
            'priority_request',
            vehicle_id,
            f'Priority granted for {len(route_intersections)} intersections'
        )
        
        return {
            'status': 'priority_granted',
            'vehicle_id': vehicle_id,
            'intersections_affected': len(route_intersections),
            'grants': priority_grants,
            'estimated_time_saved': len(route_intersections) * 30  # seconds
        }
    
    def broadcast_alert(
        self,
        alert_type: str,
        message: str,
        location: Tuple[float, float],
        radius: int = 1000
    ) -> Dict:
        """
        Broadcast alert to vehicles in area (V2X communication)
        
        Alert types: accident, hazard, construction, weather, emergency
        """
        affected_vehicles = self._find_vehicles_in_radius(location, radius)
        
        alert_data = {
            'alert_id': f'ALERT_{int(datetime.now().timestamp())}',
            'alert_type': alert_type,
            'message': message,
            'location': {'lat': location[0], 'lng': location[1]},
            'radius': radius,
            'severity': self._calculate_alert_severity(alert_type),
            'timestamp': datetime.now().isoformat(),
            'vehicles_notified': len(affected_vehicles)
        }
        
        # Send to affected vehicles
        for vehicle_id in affected_vehicles:
            self._send_alert_to_vehicle(vehicle_id, alert_data)
        
        self._log_communication(
            'alert_broadcast',
            'SYSTEM',
            f'{alert_type} alert sent to {len(affected_vehicles)} vehicles'
        )
        
        return alert_data
    
    def optimize_traffic_flow(self, road_segment_id: str) -> Dict:
        """
        Optimize traffic flow for a road segment using V2I data
        """
        vehicles_in_segment = self._get_vehicles_in_segment(road_segment_id)
        
        if not vehicles_in_segment:
            return {'error': 'No vehicles in segment'}
        
        # Calculate current metrics
        avg_speed = np.mean([v.get('speed', 50) for v in vehicles_in_segment])
        vehicle_density = len(vehicles_in_segment)
        
        # Determine optimization strategy
        if vehicle_density > 20:
            strategy = 'redistribute'
            action = 'Suggest alternative routes to reduce density'
        elif avg_speed < 30:
            strategy = 'accelerate'
            action = 'Adjust signal timing to improve flow'
        else:
            strategy = 'maintain'
            action = 'Current flow is optimal'
        
        # Calculate optimal signal timing
        optimal_green_time = self._calculate_optimal_green_time(
            vehicle_density,
            avg_speed
        )
        
        optimization_result = {
            'road_segment_id': road_segment_id,
            'vehicles_analyzed': vehicle_density,
            'current_avg_speed': round(avg_speed, 2),
            'strategy': strategy,
            'action': action,
            'optimal_green_time': optimal_green_time,
            'expected_improvement': f'{random.randint(10, 30)}%',
            'timestamp': datetime.now().isoformat()
        }
        
        self._log_communication(
            'flow_optimization',
            road_segment_id,
            f'Optimization: {strategy}'
        )
        
        return optimization_result
    
    def get_v2v_communication_status(
        self,
        vehicle_id: str
    ) -> Dict:
        """
        Get V2V communication status for a vehicle
        """
        if vehicle_id not in self.registered_vehicles:
            return {'error': 'Vehicle not registered'}
        
        vehicle = self.registered_vehicles[vehicle_id]
        nearby_vehicles = self._find_nearby_vehicles(
            vehicle_id,
            self.v2v_range
        )
        
        return {
            'vehicle_id': vehicle_id,
            'communication_mode': vehicle['communication_mode'],
            'nearby_vehicles': len(nearby_vehicles),
            'v2v_active_connections': nearby_vehicles,
            'signal_strength': vehicle['signal_strength'],
            'latency': vehicle['latency'],
            'bandwidth': vehicle['bandwidth'],
            'packet_loss': round(random.uniform(0, 2), 2)  # %
        }
    
    def _determine_priority(self, vehicle_type: str) -> int:
        """Determine vehicle priority level (0-10)"""
        priority_map = {
            'ambulance': 10,
            'fire_truck': 10,
            'police': 9,
            'bus': 6,
            'truck': 4,
            'car': 3,
            'motorcycle': 3
        }
        return priority_map.get(vehicle_type.lower(), 3)
    
    def _assign_communication_mode(self, vehicle_type: str) -> str:
        """Assign communication mode based on vehicle type"""
        if vehicle_type.lower() in ['ambulance', 'fire_truck', 'police']:
            return 'V2I'  # Infrastructure communication for priority
        else:
            return random.choice(['V2V', 'V2I', 'V2X'])
    
    def _assign_network_slice(self, vehicle_type: str) -> str:
        """
        Assign 5G/6G network slice type
        
        - URLLC: Ultra-Reliable Low-Latency (emergency vehicles)
        - eMBB: Enhanced Mobile Broadband (general vehicles)
        - mMTC: Massive Machine Type Communication (IoT sensors)
        """
        if vehicle_type.lower() in ['ambulance', 'fire_truck', 'police']:
            return 'URLLC'
        else:
            return random.choice(['eMBB', 'mMTC'])
    
    def _allocate_bandwidth(self, vehicle_type: str) -> int:
        """Allocate bandwidth in Mbps"""
        if vehicle_type.lower() in ['ambulance', 'fire_truck', 'police']:
            return random.randint(200, 300)  # High bandwidth
        else:
            return random.randint(50, 150)
    
    def _identify_route_intersections(
        self,
        start: Dict[str, float],
        end: Dict[str, float]
    ) -> List[str]:
        """Identify intersections along route"""
        # Simplified - in production, use actual route data
        num_intersections = random.randint(3, 8)
        return [f'INT_{i:03d}' for i in range(num_intersections)]
    
    def _grant_signal_priority(
        self,
        vehicle_id: str,
        intersection_id: str
    ) -> Dict:
        """Grant signal priority at intersection"""
        grant_id = f'GRANT_{intersection_id}_{vehicle_id}'
        
        self.active_signals[grant_id] = {
            'vehicle_id': vehicle_id,
            'intersection_id': intersection_id,
            'granted_at': datetime.now().isoformat(),
            'duration': 120,  # seconds
            'status': 'active'
        }
        
        return {
            'grant_id': grant_id,
            'intersection_id': intersection_id,
            'status': 'granted'
        }
    
    def _find_vehicles_in_radius(
        self,
        location: Tuple[float, float],
        radius: int
    ) -> List[str]:
        """Find vehicles within radius of location"""
        affected = []
        for vehicle_id, vehicle in self.registered_vehicles.items():
            v_loc = vehicle['location']
            distance = self._calculate_distance(
                location[0], location[1],
                v_loc['lat'], v_loc['lng']
            )
            if distance <= radius:
                affected.append(vehicle_id)
        return affected
    
    def _find_nearby_vehicles(
        self,
        vehicle_id: str,
        range_meters: int
    ) -> List[str]:
        """Find vehicles within V2V range"""
        if vehicle_id not in self.registered_vehicles:
            return []
        
        vehicle = self.registered_vehicles[vehicle_id]
        v_loc = vehicle['location']
        
        nearby = []
        for other_id, other_vehicle in self.registered_vehicles.items():
            if other_id == vehicle_id:
                continue
            
            o_loc = other_vehicle['location']
            distance = self._calculate_distance(
                v_loc['lat'], v_loc['lng'],
                o_loc['lat'], o_loc['lng']
            )
            
            if distance <= range_meters:
                nearby.append(other_id)
        
        return nearby
    
    def _get_vehicles_in_segment(self, road_segment_id: str) -> List[Dict]:
        """Get vehicles in a road segment"""
        # Simplified - return random subset
        return random.sample(
            list(self.registered_vehicles.values()),
            k=min(random.randint(5, 25), len(self.registered_vehicles))
        )
    
    def _calculate_optimal_green_time(
        self,
        vehicle_density: int,
        avg_speed: float
    ) -> int:
        """Calculate optimal green light duration"""
        base_time = 30  # seconds
        
        # Increase for high density
        density_factor = min(vehicle_density / 10, 2.0)
        
        # Adjust for speed
        speed_factor = 1.0 if avg_speed > 40 else 1.3
        
        optimal_time = int(base_time * density_factor * speed_factor)
        return min(optimal_time, 90)  # Cap at 90 seconds
    
    def _calculate_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calculate distance between two points in meters"""
        # Haversine formula
        R = 6371000  # Earth radius in meters
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lng = np.radians(lng2 - lng1)
        
        a = (np.sin(delta_lat / 2) ** 2 +
             np.cos(lat1_rad) * np.cos(lat2_rad) *
             np.sin(delta_lng / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c
    
    def _calculate_alert_severity(self, alert_type: str) -> str:
        """Calculate alert severity level"""
        severity_map = {
            'accident': 'high',
            'emergency': 'critical',
            'hazard': 'high',
            'construction': 'medium',
            'weather': 'medium'
        }
        return severity_map.get(alert_type.lower(), 'low')
    
    def _send_alert_to_vehicle(self, vehicle_id: str, alert_data: Dict):
        """Send alert to specific vehicle"""
        if vehicle_id in self.registered_vehicles:
            # In production, this would send actual message
            pass
    
    def _log_communication(self, event_type: str, entity_id: str, message: str):
        """Log communication event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'entity_id': entity_id,
            'message': message
        }
        self.communication_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.communication_log) > 1000:
            self.communication_log = self.communication_log[-1000:]
