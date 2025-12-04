"""
Demo Data Generator for Sanchar AI
Generates realistic terrain-based pothole and accident detections for demos
"""
import sqlite3
from datetime import datetime, timedelta
import random
import json

class DemoDataGenerator:
    """Generate demo data for presentations and testing"""
    
    # Major cities in India with realistic coordinates
    DEMO_LOCATIONS = [
        # Bangalore
        {"city": "Bangalore", "lat": 12.9716, "lng": 77.5946, "name": "MG Road"},
        {"city": "Bangalore", "lat": 12.9352, "lng": 77.6245, "name": "Indiranagar"},
        {"city": "Bangalore", "lat": 12.9279, "lng": 77.6271, "name": "Koramangala"},
        {"city": "Bangalore", "lat": 13.0358, "lng": 77.5970, "name": "Hebbal"},
        {"city": "Bangalore", "lat": 12.9698, "lng": 77.7499, "name": "Whitefield"},
        
        # Mumbai
        {"city": "Mumbai", "lat": 19.0760, "lng": 72.8777, "name": "Mumbai Central"},
        {"city": "Mumbai", "lat": 19.0596, "lng": 72.8295, "name": "Bandra"},
        {"city": "Mumbai", "lat": 18.9220, "lng": 72.8347, "name": "Andheri"},
        
        # Delhi
        {"city": "Delhi", "lat": 28.6139, "lng": 77.2090, "name": "Connaught Place"},
        {"city": "Delhi", "lat": 28.5355, "lng": 77.3910, "name": "Noida"},
        {"city": "Delhi", "lat": 28.4595, "lng": 77.0266, "name": "Gurgaon"},
    ]
    
    # Terrain types that affect pothole probability
    TERRAIN_TYPES = [
        {"type": "urban_main_road", "pothole_prob": 0.15, "severity": "medium"},
        {"type": "rural_road", "pothole_prob": 0.45, "severity": "high"},
        {"type": "highway", "pothole_prob": 0.08, "severity": "low"},
        {"type": "residential", "pothole_prob": 0.25, "severity": "medium"},
        {"type": "industrial", "pothole_prob": 0.35, "severity": "high"},
    ]
    
    def __init__(self, db_path='complaints.db'):
        self.db_path = db_path
        self.init_demo_tables()
    
    def init_demo_tables(self):
        """Initialize demo-specific database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Add terrain analysis table
        c.execute('''CREATE TABLE IF NOT EXISTS terrain_analysis
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      location_id INTEGER,
                      terrain_type TEXT,
                      elevation REAL,
                      slope REAL,
                      surface_roughness REAL,
                      water_drainage_score REAL,
                      pothole_risk_score REAL,
                      last_inspection TEXT,
                      FOREIGN KEY (location_id) REFERENCES complaints(id))''')
        
        # Add road quality metrics table
        c.execute('''CREATE TABLE IF NOT EXISTS road_quality
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      road_name TEXT,
                      city TEXT,
                      latitude REAL,
                      longitude REAL,
                      quality_score REAL,
                      last_maintenance TEXT,
                      traffic_volume TEXT,
                      weather_exposure TEXT)''')
        
        conn.commit()
        conn.close()
    
    def generate_demo_detections(self, count=50):
        """Generate realistic demo detection data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        generated = []
        now = datetime.now()
        
        for i in range(count):
            # Select random location
            location = random.choice(self.DEMO_LOCATIONS)
            terrain = random.choice(self.TERRAIN_TYPES)
            
            # Add slight coordinate variation for realism
            lat = location['lat'] + random.uniform(-0.02, 0.02)
            lng = location['lng'] + random.uniform(-0.02, 0.02)
            
            # Determine detection type based on terrain
            is_pothole = random.random() < terrain['pothole_prob']
            detection_type = 'pothole' if is_pothole else 'accident'
            
            # Generate confidence based on terrain and detection type
            if detection_type == 'pothole':
                confidence = random.uniform(0.75, 0.98) if terrain['severity'] == 'high' else random.uniform(0.65, 0.88)
            else:
                confidence = random.uniform(0.70, 0.95)
            
            # Create timestamp (spread over last 30 days)
            timestamp = (now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate address
            address = f"{location['name']}, {location['city']}"
            
            # Insert detection
            c.execute('''INSERT INTO complaints 
                        (detection_type, confidence, timestamp, location, description, 
                         image_path, latitude, longitude, address)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (detection_type, confidence, timestamp, address,
                      f"AI-detected {detection_type} on {terrain['type'].replace('_', ' ')}",
                      None, lat, lng, address))
            
            detection_id = c.lastrowid
            
            # Generate terrain analysis
            elevation = random.uniform(500, 1000)  # meters
            slope = random.uniform(0, 15) if terrain['type'] != 'highway' else random.uniform(0, 5)
            roughness = random.uniform(0.3, 0.9) if terrain['severity'] == 'high' else random.uniform(0.1, 0.4)
            drainage = random.uniform(0.2, 0.8)
            risk_score = (roughness * 0.4 + (1 - drainage) * 0.3 + (slope / 15) * 0.3) * 100
            
            c.execute('''INSERT INTO terrain_analysis
                        (location_id, terrain_type, elevation, slope, surface_roughness,
                         water_drainage_score, pothole_risk_score, last_inspection)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (detection_id, terrain['type'], elevation, slope, roughness,
                      drainage, risk_score, timestamp))
            
            generated.append({
                'id': detection_id,
                'type': detection_type,
                'location': address,
                'confidence': confidence,
                'terrain': terrain['type'],
                'risk_score': risk_score
            })
        
        conn.commit()
        conn.close()
        
        return generated
    
    def generate_road_quality_data(self):
        """Generate road quality assessment data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for location in self.DEMO_LOCATIONS:
            quality_score = random.uniform(50, 95)
            last_maintenance = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
            traffic_volume = random.choice(['Low', 'Medium', 'High', 'Very High'])
            weather_exposure = random.choice(['Low', 'Medium', 'High'])
            
            c.execute('''INSERT INTO road_quality
                        (road_name, city, latitude, longitude, quality_score,
                         last_maintenance, traffic_volume, weather_exposure)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (location['name'], location['city'], location['lat'], location['lng'],
                      quality_score, last_maintenance, traffic_volume, weather_exposure))
        
        conn.commit()
        conn.close()
    
    def get_terrain_heatmap_data(self):
        """Get data for terrain-based risk heatmap"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT c.latitude, c.longitude, t.pothole_risk_score, t.terrain_type
                    FROM complaints c
                    JOIN terrain_analysis t ON c.id = t.location_id
                    WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL''')
        
        results = c.fetchall()
        conn.close()
        
        return [{'lat': r[0], 'lng': r[1], 'risk': r[2], 'terrain': r[3]} for r in results]
    
    def get_demo_statistics(self):
        """Get demo statistics for presentations"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        stats = {}
        
        # Total detections
        c.execute("SELECT COUNT(*) FROM complaints")
        stats['total_detections'] = c.fetchone()[0]
        
        # Detections by type
        c.execute("SELECT detection_type, COUNT(*) FROM complaints GROUP BY detection_type")
        stats['by_type'] = dict(c.fetchall())
        
        # High-risk areas
        c.execute('''SELECT COUNT(*) FROM terrain_analysis 
                    WHERE pothole_risk_score > 70''')
        stats['high_risk_areas'] = c.fetchone()[0]
        
        # Average risk score
        c.execute("SELECT AVG(pothole_risk_score) FROM terrain_analysis")
        stats['avg_risk_score'] = round(c.fetchone()[0] or 0, 2)
        
        # Terrain distribution
        c.execute('''SELECT terrain_type, COUNT(*) FROM terrain_analysis 
                    GROUP BY terrain_type''')
        stats['terrain_distribution'] = dict(c.fetchall())
        
        conn.close()
        return stats
    
    def clear_demo_data(self):
        """Clear all demo data (useful for resetting demos)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("DELETE FROM complaints")
        c.execute("DELETE FROM terrain_analysis")
        c.execute("DELETE FROM road_quality")
        
        conn.commit()
        conn.close()
        print("✅ Demo data cleared")

def main():
    """Run demo data generation"""
    print("🎬 Sanchar AI Demo Data Generator\n")
    
    generator = DemoDataGenerator()
    
    # Clear existing demo data
    print("Clearing existing data...")
    generator.clear_demo_data()
    
    # Generate new demo data
    print("Generating demo detections...")
    detections = generator.generate_demo_detections(count=75)
    print(f"✅ Generated {len(detections)} detections")
    
    print("\nGenerating road quality data...")
    generator.generate_road_quality_data()
    print("✅ Road quality data generated")
    
    # Show statistics
    print("\n📊 Demo Statistics:")
    stats = generator.get_demo_statistics()
    print(f"   Total Detections: {stats['total_detections']}")
    print(f"   Potholes: {stats['by_type'].get('pothole', 0)}")
    print(f"   Accidents: {stats['by_type'].get('accident', 0)}")
    print(f"   High-Risk Areas: {stats['high_risk_areas']}")
    print(f"   Average Risk Score: {stats['avg_risk_score']}")
    
    print("\n🎉 Demo data generation complete!")
    print("💡 Run 'python app.py' to see the data in action")

if __name__ == '__main__':
    main()
