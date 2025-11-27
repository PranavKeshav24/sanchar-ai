"""
Google Maps Integration Service
Provides real-time mapping, routing, and geolocation services
"""
import googlemaps
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

class GoogleMapsService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY')
        self.gmaps = googlemaps.Client(key=self.api_key) if self.api_key else None
        self.geolocator = Nominatim(user_agent="sanchar-ai-traffic-system")
        
    def geocode_address(self, address):
        """Convert address to coordinates"""
        try:
            if self.gmaps:
                result = self.gmaps.geocode(address)
                if result:
                    location = result[0]['geometry']['location']
                    return {
                        'lat': location['lat'],
                        'lng': location['lng'],
                        'formatted_address': result[0]['formatted_address']
                    }
            else:
                # Fallback to geopy
                location = self.geolocator.geocode(address)
                if location:
                    return {
                        'lat': location.latitude,
                        'lng': location.longitude,
                        'formatted_address': location.address
                    }
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None
    
    def reverse_geocode(self, lat, lng):
        """Convert coordinates to address"""
        try:
            if self.gmaps:
                result = self.gmaps.reverse_geocode((lat, lng))
                if result:
                    return result[0]['formatted_address']
            else:
                # Fallback to geopy
                location = self.geolocator.reverse(f"{lat}, {lng}")
                if location:
                    return location.address
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
        return f"Location: {lat:.6f}, {lng:.6f}"
    
    def get_route(self, origin, destination, mode='driving'):
        """Get route between two points"""
        try:
            if self.gmaps:
                now = datetime.now()
                directions = self.gmaps.directions(
                    origin,
                    destination,
                    mode=mode,
                    departure_time=now,
                    traffic_model='best_guess'
                )
                
                if directions:
                    route = directions[0]
                    leg = route['legs'][0]
                    
                    # Extract polyline points
                    polyline_points = []
                    for step in leg['steps']:
                        polyline = step['polyline']['points']
                        decoded = googlemaps.convert.decode_polyline(polyline)
                        polyline_points.extend(decoded)
                    
                    return {
                        'distance': leg['distance']['text'],
                        'distance_value': leg['distance']['value'],
                        'duration': leg['duration']['text'],
                        'duration_value': leg['duration']['value'],
                        'duration_in_traffic': leg.get('duration_in_traffic', {}).get('text'),
                        'start_address': leg['start_address'],
                        'end_address': leg['end_address'],
                        'polyline': polyline_points,
                        'steps': [
                            {
                                'instruction': step['html_instructions'],
                                'distance': step['distance']['text'],
                                'duration': step['duration']['text'],
                                'start_location': step['start_location'],
                                'end_location': step['end_location']
                            }
                            for step in leg['steps']
                        ]
                    }
        except Exception as e:
            print(f"Route calculation error: {e}")
        return None
    
    def get_distance_matrix(self, origins, destinations, mode='driving'):
        """Get distance and time between multiple points"""
        try:
            if self.gmaps:
                result = self.gmaps.distance_matrix(
                    origins,
                    destinations,
                    mode=mode,
                    departure_time=datetime.now(),
                    traffic_model='best_guess'
                )
                return result
        except Exception as e:
            print(f"Distance matrix error: {e}")
        return None
    
    def get_nearby_places(self, lat, lng, place_type='hospital', radius=5000):
        """Find nearby places of a specific type"""
        try:
            if self.gmaps:
                result = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=radius,
                    type=place_type
                )
                
                places = []
                for place in result.get('results', []):
                    places.append({
                        'name': place['name'],
                        'address': place.get('vicinity', ''),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'rating': place.get('rating'),
                        'place_id': place['place_id']
                    })
                return places
        except Exception as e:
            print(f"Nearby places error: {e}")
        return []
    
    def get_elevation(self, lat, lng):
        """Get elevation at a specific location"""
        try:
            if self.gmaps:
                result = self.gmaps.elevation((lat, lng))
                if result:
                    return result[0]['elevation']
        except Exception as e:
            print(f"Elevation error: {e}")
        return None
    
    def calculate_eta(self, current_location, destination, speed_kmh=60):
        """Calculate estimated time of arrival"""
        try:
            # Get route information
            route = self.get_route(current_location, destination)
            if route:
                # Use traffic-aware duration if available
                if route.get('duration_in_traffic'):
                    return {
                        'eta_minutes': route['duration_value'] / 60,
                        'distance_km': route['distance_value'] / 1000,
                        'with_traffic': True
                    }
                else:
                    return {
                        'eta_minutes': route['duration_value'] / 60,
                        'distance_km': route['distance_value'] / 1000,
                        'with_traffic': False
                    }
        except Exception as e:
            print(f"ETA calculation error: {e}")
        return None
    
    def get_traffic_info(self, lat, lng, radius=1000):
        """Get current traffic information for an area"""
        try:
            # Note: This would require Places API or Roads API
            # For now, return simulated data or use alternative methods
            return {
                'congestion_level': 'moderate',
                'estimated_delay': '5-10 minutes'
            }
        except Exception as e:
            print(f"Traffic info error: {e}")
        return None

    def optimize_route_for_emergency(self, origin, destination, waypoints=None):
        """Optimize route for emergency vehicles avoiding traffic"""
        try:
            if self.gmaps:
                alternatives = []
                
                # Get primary route
                primary = self.get_route(origin, destination, mode='driving')
                if primary:
                    alternatives.append({
                        'name': 'Primary Route',
                        'route': primary,
                        'priority': 1
                    })
                
                # Get alternative routes
                directions = self.gmaps.directions(
                    origin,
                    destination,
                    mode='driving',
                    alternatives=True,
                    departure_time=datetime.now()
                )
                
                for idx, route in enumerate(directions[1:], start=2):
                    leg = route['legs'][0]
                    polyline_points = []
                    for step in leg['steps']:
                        decoded = googlemaps.convert.decode_polyline(step['polyline']['points'])
                        polyline_points.extend(decoded)
                    
                    alternatives.append({
                        'name': f'Alternative Route {idx-1}',
                        'route': {
                            'distance': leg['distance']['text'],
                            'distance_value': leg['distance']['value'],
                            'duration': leg['duration']['text'],
                            'duration_value': leg['duration']['value'],
                            'polyline': polyline_points
                        },
                        'priority': idx
                    })
                
                # Sort by duration (fastest first)
                alternatives.sort(key=lambda x: x['route']['duration_value'])
                
                return alternatives
        except Exception as e:
            print(f"Emergency route optimization error: {e}")
        return None


class EmergencyVehicleTracker:
    """Track emergency vehicles in real-time"""
    
    def __init__(self, maps_service):
        self.maps_service = maps_service
        self.active_vehicles = {}
        
    def register_vehicle(self, vehicle_id, vehicle_type, current_location, destination):
        """Register an emergency vehicle for tracking"""
        route = self.maps_service.optimize_route_for_emergency(
            current_location,
            destination
        )
        
        self.active_vehicles[vehicle_id] = {
            'id': vehicle_id,
            'type': vehicle_type,
            'status': 'active',
            'current_location': current_location,
            'destination': destination,
            'route': route[0] if route else None,
            'alternative_routes': route[1:] if route and len(route) > 1 else [],
            'registered_at': datetime.now(),
            'eta': None
        }
        
        # Calculate ETA
        if route:
            eta = self.maps_service.calculate_eta(current_location, destination)
            self.active_vehicles[vehicle_id]['eta'] = eta
        
        return self.active_vehicles[vehicle_id]
    
    def update_vehicle_location(self, vehicle_id, new_location):
        """Update vehicle's current location"""
        if vehicle_id in self.active_vehicles:
            vehicle = self.active_vehicles[vehicle_id]
            vehicle['current_location'] = new_location
            
            # Recalculate ETA
            eta = self.maps_service.calculate_eta(
                new_location,
                vehicle['destination']
            )
            vehicle['eta'] = eta
            
            return vehicle
        return None
    
    def get_vehicle_status(self, vehicle_id):
        """Get current status of an emergency vehicle"""
        return self.active_vehicles.get(vehicle_id)
    
    def complete_journey(self, vehicle_id):
        """Mark vehicle journey as complete"""
        if vehicle_id in self.active_vehicles:
            self.active_vehicles[vehicle_id]['status'] = 'completed'
            self.active_vehicles[vehicle_id]['completed_at'] = datetime.now()
        
    def get_all_active_vehicles(self):
        """Get all active emergency vehicles"""
        return [v for v in self.active_vehicles.values() if v['status'] == 'active']
