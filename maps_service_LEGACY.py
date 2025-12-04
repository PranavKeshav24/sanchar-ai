"""
Open Source Maps Integration Service
Uses free and open-source alternatives:
- OpenStreetMap (Nominatim) for geocoding
- OSRM (Open Source Routing Machine) for routing
- Overpass API for POI search
- Open-Elevation API for elevation data
- CesiumJS for 3D visualization (frontend)

NO API KEYS REQUIRED - 100% Free and Open Source!
"""
import os
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import polyline


class OpenMapsService:
    """
    Open-source maps service using free APIs:
    - Nominatim (OpenStreetMap) for geocoding
    - OSRM for routing
    - Overpass API for nearby places
    """
    
    def __init__(self, api_key=None):
        # API key not needed for open-source services
        self.geolocator = Nominatim(user_agent="sanchar-ai-traffic-system")
        self.osrm_url = "https://router.project-osrm.org"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.elevation_url = "https://api.open-elevation.com/api/v1/lookup"
        
    def geocode_address(self, address):
        """Convert address to coordinates using Nominatim (OpenStreetMap)"""
        try:
            location = self.geolocator.geocode(address, addressdetails=True)
            if location:
                return {
                    'lat': location.latitude,
                    'lng': location.longitude,
                    'formatted_address': location.address,
                    'display_name': location.raw.get('display_name', location.address)
                }
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None
    
    def reverse_geocode(self, lat, lng):
        """Convert coordinates to address using Nominatim"""
        try:
            location = self.geolocator.reverse(f"{lat}, {lng}", language='en')
            if location:
                return location.address
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
        return f"Location: {lat:.6f}, {lng:.6f}"
    
    def get_route(self, origin, destination, mode='driving'):
        """
        Get route between two points using OSRM (Open Source Routing Machine)
        Supports: driving, walking, cycling
        """
        try:
            # Convert origin/destination to coordinates if they're addresses
            origin_coords = self._get_coordinates(origin)
            dest_coords = self._get_coordinates(destination)
            
            if not origin_coords or not dest_coords:
                return None
            
            # OSRM profile mapping
            profile_map = {
                'driving': 'car',
                'car': 'car',
                'walking': 'foot',
                'foot': 'foot',
                'cycling': 'bike',
                'bike': 'bike'
            }
            profile = profile_map.get(mode, 'car')
            
            # Call OSRM API
            url = f"{self.osrm_url}/route/v1/{profile}/{origin_coords['lng']},{origin_coords['lat']};{dest_coords['lng']},{dest_coords['lat']}"
            params = {
                'overview': 'full',
                'geometries': 'polyline',
                'steps': 'true',
                'annotations': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                leg = route['legs'][0]
                
                # Decode polyline to coordinates
                decoded_polyline = polyline.decode(route['geometry'])
                polyline_points = [{'lat': lat, 'lng': lng} for lat, lng in decoded_polyline]
                
                # Extract turn-by-turn directions
                steps = []
                for step in leg.get('steps', []):
                    maneuver = step.get('maneuver', {})
                    steps.append({
                        'instruction': self._format_instruction(step),
                        'distance': self._format_distance(step.get('distance', 0)),
                        'duration': self._format_duration(step.get('duration', 0)),
                        'start_location': {
                            'lat': maneuver.get('location', [0, 0])[1],
                            'lng': maneuver.get('location', [0, 0])[0]
                        },
                        'type': maneuver.get('type', 'continue'),
                        'modifier': maneuver.get('modifier', '')
                    })
                
                return {
                    'distance': self._format_distance(route['distance']),
                    'distance_value': route['distance'],  # in meters
                    'duration': self._format_duration(route['duration']),
                    'duration_value': route['duration'],  # in seconds
                    'start_address': origin if isinstance(origin, str) else f"{origin_coords['lat']}, {origin_coords['lng']}",
                    'end_address': destination if isinstance(destination, str) else f"{dest_coords['lat']}, {dest_coords['lng']}",
                    'polyline': polyline_points,
                    'steps': steps,
                    'summary': leg.get('summary', '')
                }
                
        except Exception as e:
            print(f"Route calculation error: {e}")
        return None
    
    def _get_coordinates(self, location):
        """Convert location (address or coords) to coordinates dict"""
        if isinstance(location, dict):
            return location
        if isinstance(location, str):
            # Check if it's already coordinates
            if ',' in location:
                try:
                    parts = location.split(',')
                    return {'lat': float(parts[0].strip()), 'lng': float(parts[1].strip())}
                except ValueError:
                    pass
            # It's an address, geocode it
            return self.geocode_address(location)
        return None
    
    def _format_distance(self, meters):
        """Format distance in human-readable format"""
        if meters < 1000:
            return f"{int(meters)} m"
        return f"{meters/1000:.1f} km"
    
    def _format_duration(self, seconds):
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)} sec"
        elif seconds < 3600:
            return f"{int(seconds/60)} min"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours} hr {minutes} min"
    
    def _format_instruction(self, step):
        """Format OSRM step into human-readable instruction"""
        maneuver = step.get('maneuver', {})
        step_type = maneuver.get('type', 'continue')
        modifier = maneuver.get('modifier', '')
        name = step.get('name', 'the road')
        
        if step_type == 'depart':
            return f"Start on {name}"
        elif step_type == 'arrive':
            return "Arrive at your destination"
        elif step_type == 'turn':
            return f"Turn {modifier} onto {name}"
        elif step_type == 'new name':
            return f"Continue onto {name}"
        elif step_type == 'merge':
            return f"Merge {modifier} onto {name}"
        elif step_type == 'roundabout':
            exit_num = maneuver.get('exit', 1)
            return f"Enter roundabout, take exit {exit_num} onto {name}"
        else:
            return f"Continue on {name}"
    
    def get_distance_matrix(self, origins, destinations, mode='driving'):
        """Get distance and time between multiple points using OSRM Table service"""
        try:
            # Collect all coordinates
            all_coords = []
            origin_indices = []
            dest_indices = []
            
            for i, origin in enumerate(origins):
                coords = self._get_coordinates(origin)
                if coords:
                    origin_indices.append(len(all_coords))
                    all_coords.append(coords)
            
            for i, dest in enumerate(destinations):
                coords = self._get_coordinates(dest)
                if coords:
                    dest_indices.append(len(all_coords))
                    all_coords.append(coords)
            
            if not all_coords:
                return None
            
            # Build coordinates string
            coords_str = ";".join([f"{c['lng']},{c['lat']}" for c in all_coords])
            
            profile = 'car' if mode == 'driving' else 'foot' if mode == 'walking' else 'bike'
            url = f"{self.osrm_url}/table/v1/{profile}/{coords_str}"
            params = {
                'sources': ';'.join(map(str, origin_indices)),
                'destinations': ';'.join(map(str, dest_indices)),
                'annotations': 'duration,distance'
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('code') == 'Ok':
                return {
                    'durations': data.get('durations', []),
                    'distances': data.get('distances', []),
                    'origins': origins,
                    'destinations': destinations
                }
                
        except Exception as e:
            print(f"Distance matrix error: {e}")
        return None
    
    def get_nearby_places(self, lat, lng, place_type='hospital', radius=5000):
        """
        Find nearby places using Overpass API (OpenStreetMap)
        Supported types: hospital, police, fire_station, pharmacy, school, restaurant
        """
        try:
            # Map place types to OSM tags
            osm_tags = {
                'hospital': 'amenity=hospital',
                'police': 'amenity=police',
                'fire_station': 'amenity=fire_station',
                'pharmacy': 'amenity=pharmacy',
                'school': 'amenity=school',
                'restaurant': 'amenity=restaurant',
                'fuel': 'amenity=fuel',
                'bank': 'amenity=bank',
                'atm': 'amenity=atm',
                'parking': 'amenity=parking'
            }
            
            tag = osm_tags.get(place_type, f'amenity={place_type}')
            
            # Overpass QL query
            query = f"""
            [out:json][timeout:25];
            (
              node[{tag}](around:{radius},{lat},{lng});
              way[{tag}](around:{radius},{lat},{lng});
              relation[{tag}](around:{radius},{lat},{lng});
            );
            out center;
            """
            
            response = requests.post(self.overpass_url, data={'data': query}, timeout=30)
            data = response.json()
            
            places = []
            for element in data.get('elements', []):
                # Get coordinates (center for ways/relations)
                if element['type'] == 'node':
                    place_lat = element['lat']
                    place_lng = element['lon']
                else:
                    center = element.get('center', {})
                    place_lat = center.get('lat')
                    place_lng = center.get('lon')
                
                if place_lat and place_lng:
                    tags = element.get('tags', {})
                    name = tags.get('name', tags.get('operator', f'Unnamed {place_type.title()}'))
                    
                    # Calculate distance
                    distance = geodesic((lat, lng), (place_lat, place_lng)).meters
                    
                    places.append({
                        'name': name,
                        'address': self._build_address(tags),
                        'lat': place_lat,
                        'lng': place_lng,
                        'distance': distance,
                        'distance_text': self._format_distance(distance),
                        'type': place_type,
                        'phone': tags.get('phone', tags.get('contact:phone', '')),
                        'website': tags.get('website', tags.get('contact:website', '')),
                        'opening_hours': tags.get('opening_hours', '')
                    })
            
            # Sort by distance
            places.sort(key=lambda x: x['distance'])
            
            return places[:20]  # Return top 20 nearest
            
        except Exception as e:
            print(f"Nearby places error: {e}")
        return []
    
    def _build_address(self, tags):
        """Build address string from OSM tags"""
        parts = []
        if tags.get('addr:housenumber'):
            parts.append(tags['addr:housenumber'])
        if tags.get('addr:street'):
            parts.append(tags['addr:street'])
        if tags.get('addr:city'):
            parts.append(tags['addr:city'])
        if tags.get('addr:postcode'):
            parts.append(tags['addr:postcode'])
        
        return ', '.join(parts) if parts else 'Address not available'
    
    def get_elevation(self, lat, lng):
        """Get elevation at a specific location using Open-Elevation API"""
        try:
            url = f"{self.elevation_url}"
            params = {'locations': f"{lat},{lng}"}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('results'):
                return data['results'][0].get('elevation')
                
        except Exception as e:
            print(f"Elevation error: {e}")
        return None
    
    def get_multiple_elevations(self, coordinates):
        """Get elevations for multiple points (for 3D terrain)"""
        try:
            locations = [{'latitude': c['lat'], 'longitude': c['lng']} for c in coordinates]
            
            response = requests.post(
                self.elevation_url,
                json={'locations': locations},
                timeout=30
            )
            data = response.json()
            
            if data.get('results'):
                return [r.get('elevation', 0) for r in data['results']]
                
        except Exception as e:
            print(f"Multiple elevations error: {e}")
        return [0] * len(coordinates)
    
    def calculate_eta(self, current_location, destination, speed_kmh=60):
        """Calculate estimated time of arrival"""
        try:
            route = self.get_route(current_location, destination)
            if route:
                return {
                    'eta_minutes': route['duration_value'] / 60,
                    'distance_km': route['distance_value'] / 1000,
                    'duration_text': route['duration'],
                    'distance_text': route['distance']
                }
        except Exception as e:
            print(f"ETA calculation error: {e}")
        return None
    
    def get_traffic_info(self, lat, lng, radius=1000):
        """
        Get traffic-related information
        Note: Real-time traffic requires premium APIs, this provides static data
        """
        try:
            # Query for traffic-related OSM features
            query = f"""
            [out:json][timeout:25];
            (
              node["highway"="traffic_signals"](around:{radius},{lat},{lng});
              node["highway"="crossing"](around:{radius},{lat},{lng});
              way["highway"="primary"](around:{radius},{lat},{lng});
              way["highway"="secondary"](around:{radius},{lat},{lng});
            );
            out count;
            """
            
            response = requests.post(self.overpass_url, data={'data': query}, timeout=30)
            data = response.json()
            
            count = len(data.get('elements', []))
            
            # Estimate congestion based on infrastructure density
            if count > 50:
                congestion = 'high'
            elif count > 20:
                congestion = 'moderate'
            else:
                congestion = 'low'
            
            return {
                'congestion_level': congestion,
                'infrastructure_count': count,
                'note': 'Based on infrastructure density, not real-time data'
            }
        except Exception as e:
            print(f"Traffic info error: {e}")
        return None

    def optimize_route_for_emergency(self, origin, destination, waypoints=None):
        """Optimize route for emergency vehicles"""
        try:
            alternatives = []
            
            # Get primary route
            primary = self.get_route(origin, destination, mode='driving')
            if primary:
                alternatives.append({
                    'name': 'Primary Route',
                    'route': primary,
                    'priority': 1
                })
            
            # Get alternative routes using OSRM alternatives parameter
            origin_coords = self._get_coordinates(origin)
            dest_coords = self._get_coordinates(destination)
            
            if origin_coords and dest_coords:
                url = f"{self.osrm_url}/route/v1/car/{origin_coords['lng']},{origin_coords['lat']};{dest_coords['lng']},{dest_coords['lat']}"
                params = {
                    'overview': 'full',
                    'geometries': 'polyline',
                    'steps': 'true',
                    'alternatives': 'true'
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if data.get('code') == 'Ok':
                    for idx, route in enumerate(data.get('routes', [])[1:], start=2):
                        leg = route['legs'][0]
                        decoded_polyline = polyline.decode(route['geometry'])
                        polyline_points = [{'lat': lat, 'lng': lng} for lat, lng in decoded_polyline]
                        
                        alternatives.append({
                            'name': f'Alternative Route {idx-1}',
                            'route': {
                                'distance': self._format_distance(route['distance']),
                                'distance_value': route['distance'],
                                'duration': self._format_duration(route['duration']),
                                'duration_value': route['duration'],
                                'polyline': polyline_points
                            },
                            'priority': idx
                        })
            
            # Sort by duration (fastest first)
            alternatives.sort(key=lambda x: x['route'].get('duration_value', float('inf')))
            
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
            'registered_at': datetime.now().isoformat(),
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
            vehicle['last_updated'] = datetime.now().isoformat()
            
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
            self.active_vehicles[vehicle_id]['completed_at'] = datetime.now().isoformat()
        
    def get_all_active_vehicles(self):
        """Get all active emergency vehicles"""
        return [v for v in self.active_vehicles.values() if v['status'] == 'active']


# Backward compatibility aliases
GoogleMapsService = OpenMapsService
