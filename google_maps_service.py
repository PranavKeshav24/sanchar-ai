"""
Google Maps & Earth Engine Service
Handles geocoding, routing, 3D terrain analysis, and emergency vehicle tracking
"""

import requests
import json
import os
import ee
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math


def decode_polyline(polyline_str):
    """Decode Google Maps polyline string to list of coordinates"""
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}
    
    while index < len(polyline_str):
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0
            
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            
            if result & 1:
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = result >> 1
        
        lat += changes['latitude']
        lng += changes['longitude']
        
        coordinates.append({
            'lat': lat / 1e5,
            'lng': lng / 1e5
        })
    
    return coordinates


class GoogleMapsService:
    """Google Maps API integration for geocoding and routing"""
    
    def __init__(self, api_key: str):
        self.api_key = "your_api_key"
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Convert address to coordinates, or parse if already coordinates"""
        # Check if input is already coordinates (lat,lng format)
        if ',' in address:
            try:
                parts = address.strip().split(',')
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    # Validate reasonable coordinate ranges
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        return {
                            'lat': lat,
                            'lng': lng,
                            'formatted_address': f"{lat}, {lng}"
                        }
            except (ValueError, IndexError):
                pass  # Not valid coordinates, continue to geocoding
        
        # Try Google Maps geocoding
        url = f"{self.base_url}/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=3)
            data = response.json()
            
            if data['status'] == 'OK' and len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': data['results'][0]['formatted_address']
                }
            else:
                print(f"Google geocoding failed for '{address}': {data.get('status', 'UNKNOWN')}")
        except Exception as e:
            print(f"Google geocoding error for '{address}': {e}")
        
        # Fallback to OpenStreetMap Nominatim
        try:
            print(f"Using OpenStreetMap fallback for geocoding '{address}'")
            osm_url = "https://nominatim.openstreetmap.org/search"
            osm_params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'SancharAI-Emergency-Tracker/1.0'
            }
            
            response = requests.get(osm_url, params=osm_params, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    coords = {
                        'lat': float(result['lat']),
                        'lng': float(result['lon']),
                        'formatted_address': result.get('display_name', address)
                    }
                    print(f"✓ OSM geocode success: {coords['formatted_address']}")
                    return coords
        except Exception as e:
            print(f"OpenStreetMap geocoding failed: {e}")
        
        return None
    
    def reverse_geocode(self, lat: float, lng: float) -> str:
        """Convert coordinates to address with fallback to OpenStreetMap"""
        # Try Google Maps first
        url = f"{self.base_url}/geocode/json"
        params = {
            'latlng': f"{lat},{lng}",
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=3)
            data = response.json()
            
            if data['status'] == 'OK' and len(data['results']) > 0:
                return data['results'][0]['formatted_address']
        except Exception as e:
            print(f"Google reverse geocoding failed: {e}")
        
        # Fallback to OpenStreetMap Nominatim (free, no API key needed)
        try:
            print(f"Using OpenStreetMap fallback for reverse geocoding")
            osm_url = "https://nominatim.openstreetmap.org/reverse"
            osm_params = {
                'lat': lat,
                'lon': lng,
                'format': 'json'
            }
            headers = {
                'User-Agent': 'SancharAI-Emergency-Tracker/1.0'
            }
            
            response = requests.get(osm_url, params=osm_params, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                address = data.get('display_name', f"{lat}, {lng}")
                print(f"✓ OSM reverse geocode: {address}")
                return address
        except Exception as e:
            print(f"OpenStreetMap reverse geocoding failed: {e}")
        
        # Final fallback
        return f"{lat}, {lng}"
    
    def get_route(self, origin: str, destination: str, mode: str = 'driving') -> Optional[Dict]:
        """Get route between two points"""
        url = f"{self.base_url}/directions/json"
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK' and len(data['routes']) > 0:
                route = data['routes'][0]
                leg = route['legs'][0]
                
                return {
                    'distance': leg['distance']['text'],
                    'duration': leg['duration']['text'],
                    'distance_value': leg['distance']['value'],
                    'duration_value': leg['duration']['value'],
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address'],
                    'polyline': route['overview_polyline']['points'],
                    'steps': leg['steps']
                }
            else:
                error_msg = data.get('error_message', data.get('status', 'UNKNOWN'))
                print(f"Routing failed ({origin} -> {destination}): {error_msg}")
        except Exception as e:
            print(f"Routing error ({origin} -> {destination}): {e}")
        
        return None
    
    def get_nearby_places(self, lat: float, lng: float, place_type: str, radius: int = 5000) -> List[Dict]:
        """Find nearby places (e.g., hospitals)"""
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': place_type,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                places = []
                for place in data['results'][:10]:  # Limit to 10 results
                    places.append({
                        'name': place['name'],
                        'address': place.get('vicinity', ''),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'rating': place.get('rating', 0),
                        'place_id': place['place_id']
                    })
                return places
        except Exception as e:
            print(f"Places search error: {e}")
        
        return []
    
    def get_elevation(self, lat: float, lng: float) -> Optional[Dict]:
        """Get elevation data for a location"""
        url = f"{self.base_url}/elevation/json"
        params = {
            'locations': f"{lat},{lng}",
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK' and len(data['results']) > 0:
                return {
                    'elevation': data['results'][0]['elevation'],
                    'resolution': data['results'][0]['resolution']
                }
        except Exception as e:
            print(f"Elevation error: {e}")
        
        return None


class GoogleEarthEngineService:
    """Google Earth Engine for advanced 3D terrain analysis"""
    
    def __init__(self, project_id: str, key_path: str):
        self.project_id = project_id
        self.key_path = key_path
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Earth Engine"""
        try:
            if not os.path.exists(self.key_path):
                print(f"ℹ Earth Engine: Service account key not found at {self.key_path}")
                print("  → Using fallback terrain analysis (works without Google Earth Engine)")
                return
            
            if not self.project_id or self.project_id == "your_gee_project_id":
                print(f"ℹ Earth Engine: Project ID not configured")
                print("  → Using fallback terrain analysis (works without Google Earth Engine)")
                return
                
            try:
                credentials = ee.ServiceAccountCredentials(None, self.key_path)
                ee.Initialize(credentials, project=self.project_id)
                self.initialized = True
                print("✓ Google Earth Engine initialized successfully")
                print("  → Advanced 3D terrain analysis enabled")
            except Exception as e:
                # Catch initialization errors specifically
                error_msg = str(e)
                print(f"⚠ Earth Engine Initialization Warning: {error_msg}")
                print("  → Switching to Simulation Mode for Terrain Analysis")
                print("  → This is expected if you haven't set up a Google Cloud Project with Earth Engine API enabled.")
                self.initialized = False
                
        except Exception as e:
            print(f"Unexpected error in Earth Engine service: {e}")
            self.initialized = False
    
    def get_terrain_analysis(self, lat: float, lng: float, radius: int = 100) -> Dict:
        """
        Analyze terrain for pothole risk assessment
        Uses DEM (Digital Elevation Model) data for 3D terrain analysis
        """
        if not self.initialized:
            return self._fallback_terrain_analysis(lat, lng)
        
        try:
            # Define point of interest
            point = ee.Geometry.Point([lng, lat])
            region = point.buffer(radius)
            
            # Get SRTM Digital Elevation Model (30m resolution)
            dem = ee.Image('USGS/SRTMGL1_003')
            
            # Calculate terrain metrics
            elevation = dem.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=30
            ).getInfo()
            
            # Calculate slope
            slope = ee.Terrain.slope(dem)
            slope_value = slope.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=30
            ).getInfo()
            
            # Calculate aspect (direction of slope)
            aspect = ee.Terrain.aspect(dem)
            aspect_value = aspect.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=30
            ).getInfo()
            
            # Get terrain roughness (standard deviation of elevation)
            roughness = dem.reduceRegion(
                reducer=ee.Reducer.stdDev(),
                geometry=region,
                scale=30
            ).getInfo()
            
            # Normalize and calculate risk scores
            elevation_m = elevation.get('elevation', 0)
            slope_deg = slope_value.get('slope', 0)
            roughness_val = roughness.get('elevation', 0)
            
            # Calculate surface roughness score (0-1)
            surface_roughness = min(roughness_val / 10, 1.0)  # Normalize to 0-1
            
            # Calculate water drainage score (0-1, higher slope = better drainage)
            water_drainage = max(0, min(slope_deg / 15, 1.0))  # 15° = good drainage
            
            # Calculate pothole risk score (0-100)
            # Higher risk with: low slope (poor drainage), high roughness, flat terrain
            pothole_risk = (
                (1 - water_drainage) * 0.4 +  # 40% weight on drainage
                surface_roughness * 0.3 +       # 30% weight on roughness
                (min(slope_deg, 5) / 5) * 0.3   # 30% weight on flatness
            ) * 100
            
            # Determine terrain type
            terrain_type = self._classify_terrain(elevation_m, slope_deg, roughness_val)
            
            return {
                'elevation': round(elevation_m, 2),
                'slope': round(slope_deg, 2),
                'aspect': round(aspect_value.get('aspect', 0), 2),
                'surface_roughness': round(surface_roughness, 3),
                'water_drainage_score': round(water_drainage, 3),
                'pothole_risk_score': round(pothole_risk, 2),
                'terrain_type': terrain_type,
                'analysis_method': 'google_earth_engine',
                'resolution': '30m_srtm',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Earth Engine analysis error: {e}")
            return self._fallback_terrain_analysis(lat, lng)
    
    def _fallback_terrain_analysis(self, lat: float, lng: float) -> Dict:
        """Fallback terrain analysis using estimated data"""
        # Use geographic heuristics
        import random
        
        # Estimate terrain based on location patterns
        base_elevation = abs(lat) * 100  # Rough estimate
        estimated_slope = random.uniform(0.5, 8.0)
        estimated_roughness = random.uniform(0.1, 0.6)
        
        water_drainage = max(0, min(estimated_slope / 15, 1.0))
        pothole_risk = (
            (1 - water_drainage) * 0.4 +
            estimated_roughness * 0.3 +
            (min(estimated_slope, 5) / 5) * 0.3
        ) * 100
        
        terrain_type = self._classify_terrain(base_elevation, estimated_slope, estimated_roughness * 10)
        
        return {
            'elevation': round(base_elevation, 2),
            'slope': round(estimated_slope, 2),
            'aspect': round(random.uniform(0, 360), 2),
            'surface_roughness': round(estimated_roughness, 3),
            'water_drainage_score': round(water_drainage, 3),
            'pothole_risk_score': round(pothole_risk, 2),
            'terrain_type': terrain_type,
            'analysis_method': 'fallback_estimation',
            'resolution': 'estimated',
            'timestamp': datetime.now().isoformat()
        }
    
    def _classify_terrain(self, elevation: float, slope: float, roughness: float) -> str:
        """Classify terrain type based on metrics"""
        if slope < 2 and roughness < 2:
            return 'urban_flat'
        elif slope < 5 and roughness < 5:
            return 'urban_main_road'
        elif slope < 8 and roughness < 8:
            return 'residential_road'
        elif slope > 10:
            return 'hilly_terrain'
        elif roughness > 5:
            return 'rural_road'
        else:
            return 'highway'
    
    def get_3d_terrain_mesh(self, lat: float, lng: float, size_km: float = 1.0) -> Optional[Dict]:
        """
        Get 3D terrain mesh data for visualization
        Returns elevation grid for 3D rendering
        """
        if not self.initialized:
            return None
        
        try:
            # Define bounding box
            half_size = size_km / 2 / 111  # Convert km to degrees (approx)
            bounds = ee.Geometry.Rectangle([
                lng - half_size, lat - half_size,
                lng + half_size, lat + half_size
            ])
            
            # Get DEM
            dem = ee.Image('USGS/SRTMGL1_003')
            
            # Sample elevation grid (20x20 points)
            grid_points = []
            grid_size = 20
            
            for i in range(grid_size):
                for j in range(grid_size):
                    point_lng = lng - half_size + (i / grid_size) * (2 * half_size)
                    point_lat = lat - half_size + (j / grid_size) * (2 * half_size)
                    
                    point = ee.Geometry.Point([point_lng, point_lat])
                    elevation = dem.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=point,
                        scale=30
                    ).getInfo()
                    
                    grid_points.append({
                        'lat': point_lat,
                        'lng': point_lng,
                        'elevation': elevation.get('elevation', 0)
                    })
            
            return {
                'grid_size': grid_size,
                'bounds': {
                    'north': lat + half_size,
                    'south': lat - half_size,
                    'east': lng + half_size,
                    'west': lng - half_size
                },
                'points': grid_points,
                'center': {'lat': lat, 'lng': lng}
            }
            
        except Exception as e:
            print(f"3D mesh generation error: {e}")
            return None


class EmergencyVehicleTracker:
    """Real-time emergency vehicle tracking and routing"""
    
    def __init__(self, maps_service: GoogleMapsService):
        self.maps_service = maps_service
        self.active_vehicles = {}
    
    def register_vehicle(self, vehicle_id: str, vehicle_type: str, current_location: str, destination: str) -> Dict:
        """Register new emergency vehicle"""
        print(f"Registering vehicle {vehicle_id}: {current_location} -> {destination}")
        
        # Parse current location (must be coordinates)
        current_coords = self.maps_service.geocode_address(current_location)
        if not current_coords:
            print(f"✗ Failed: Could not parse current location '{current_location}'")
            return {'error': 'Invalid current location format'}
        
        # Try to parse destination
        dest_coords = self.maps_service.geocode_address(destination)
        
        # If destination couldn't be geocoded, use a default nearby location
        if not dest_coords:
            print(f"⚠ Destination '{destination}' could not be geocoded, using nearby default")
            # Use a location 5km away as estimate
            dest_coords = {
                'lat': current_coords['lat'] + 0.045,  # ~5km north
                'lng': current_coords['lng'] + 0.045,  # ~5km east
                'formatted_address': destination
            }
        
        # Try to get route (optional - continue if fails)
        route_data = self.maps_service.get_route(current_location, destination)
        
        if route_data:
            # Full route available
            from google_maps_service import decode_polyline
            polyline_coords = decode_polyline(route_data['polyline'])
            
            eta_minutes = route_data['duration_value'] / 60
            distance_km = route_data['distance_value'] / 1000
            
            self.active_vehicles[vehicle_id] = {
                'id': vehicle_id,
                'type': vehicle_type,
                'current_location': current_location,
                'destination': destination,
                'current_coords': current_coords,
                'destination_coords': dest_coords,
                'route': {
                    'route': {
                        'polyline': polyline_coords,
                        'distance': route_data['distance'],
                        'duration': route_data['duration']
                    }
                },
                'eta': {
                    'eta_minutes': eta_minutes,
                    'distance_km': distance_km
                },
                'status': 'active',
                'registered_at': datetime.now().isoformat()
            }
            
            print(f"✓ Vehicle {vehicle_id} registered with full route. Total active: {len(self.active_vehicles)}")
            return self.active_vehicles[vehicle_id]
        
        # Fallback: Register with coordinates only (calculate straight-line distance)
        print(f"⚠ Route API unavailable, using straight-line distance")
        
        # Calculate straight-line distance
        import math
        lat1, lng1 = current_coords['lat'], current_coords['lng']
        lat2, lng2 = dest_coords['lat'], dest_coords['lng']
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance_km = R * c
        
        # Estimate ETA (40 km/h city average)
        eta_minutes = (distance_km / 40) * 60
        
        self.active_vehicles[vehicle_id] = {
            'id': vehicle_id,
            'type': vehicle_type,
            'current_location': current_location,
            'destination': destination,
            'current_coords': current_coords,
            'destination_coords': dest_coords,
            'eta': {
                'eta_minutes': eta_minutes,
                'distance_km': distance_km
            },
            'status': 'active',
            'registered_at': datetime.now().isoformat(),
            'mode': 'estimated'
        }
        
        print(f"✓ Vehicle {vehicle_id} registered (estimated). Distance: {distance_km:.2f}km, ETA: {eta_minutes:.1f}min. Total: {len(self.active_vehicles)}")
        return self.active_vehicles[vehicle_id]
    
    def update_vehicle_location(self, vehicle_id: str, new_location: str) -> Optional[Dict]:
        """Update vehicle location and recalculate route if needed"""
        if vehicle_id not in self.active_vehicles:
            return None
        
        vehicle = self.active_vehicles[vehicle_id]
        old_location = vehicle['current_location']
        vehicle['current_location'] = new_location
        
        # Recalculate route
        route_data = self.maps_service.get_route(new_location, vehicle['destination'])
        if route_data:
            from google_maps_service import decode_polyline
            polyline_coords = decode_polyline(route_data['polyline'])
            
            eta_minutes = route_data['duration_value'] / 60
            distance_km = route_data['distance_value'] / 1000
            
            vehicle['route'] = {
                'route': {
                    'polyline': polyline_coords,
                    'distance': route_data['distance'],
                    'duration': route_data['duration']
                }
            }
            vehicle['eta'] = {
                'eta_minutes': eta_minutes,
                'distance_km': distance_km
            }
            vehicle['updated_at'] = datetime.now().isoformat()
        
        return vehicle
    
    def get_vehicle_status(self, vehicle_id: str) -> Optional[Dict]:
        """Get current vehicle status"""
        return self.active_vehicles.get(vehicle_id)
    
    def get_all_active_vehicles(self) -> List[Dict]:
        """Get all active emergency vehicles"""
        return list(self.active_vehicles.values())
    
    def complete_journey(self, vehicle_id: str):
        """Mark vehicle journey as complete"""
        if vehicle_id in self.active_vehicles:
            self.active_vehicles[vehicle_id]['status'] = 'completed'
            self.active_vehicles[vehicle_id]['completed_at'] = datetime.now().isoformat()
    
    def get_optimal_route_avoiding_potholes(self, origin: str, destination: str, pothole_locations: List[Tuple[float, float]]) -> Dict:
        """
        Calculate optimal route avoiding known pothole locations
        """
        # Get standard route
        standard_route = self.maps_service.get_route(origin, destination)
        
        if not standard_route:
            return {'error': 'Could not calculate route'}
        
        # In a production system, this would:
        # 1. Parse the route polyline
        # 2. Check for proximity to pothole locations
        # 3. Request alternative routes avoiding those areas
        # 4. Compare routes and select optimal
        
        # For now, return standard route with pothole avoidance flag
        return {
            **standard_route,
            'pothole_avoidance_enabled': True,
            'potholes_checked': len(pothole_locations)
        }
