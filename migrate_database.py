"""
Database Migration Script for Sanchar AI
Adds geolocation and terrain analysis support
"""
import sqlite3
import os

def migrate_database(db_path='complaints.db'):
    """Migrate database to support terrain analysis"""
    print("🔧 Starting database migration...")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if columns already exist
    c.execute('PRAGMA table_info(complaints)')
    columns = [col[1] for col in c.fetchall()]
    
    # Add missing columns to complaints table
    if 'latitude' not in columns:
        print("  Adding latitude column...")
        c.execute('ALTER TABLE complaints ADD COLUMN latitude REAL')
    
    if 'longitude' not in columns:
        print("  Adding longitude column...")
        c.execute('ALTER TABLE complaints ADD COLUMN longitude REAL')
    
    if 'address' not in columns:
        print("  Adding address column...")
        c.execute('ALTER TABLE complaints ADD COLUMN address TEXT')
    
    # Create terrain_analysis table if it doesn't exist
    print("  Creating terrain_analysis table...")
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
    
    # Create road_quality table if it doesn't exist
    print("  Creating road_quality table...")
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
    
    print("✅ Database migration complete!")
    print("   - Added latitude/longitude columns")
    print("   - Added address column")
    print("   - Created terrain_analysis table")
    print("   - Created road_quality table")

def backup_database(db_path='complaints.db'):
    """Create backup of database before migration"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")

if __name__ == '__main__':
    print("📊 Sanchar AI Database Migration Tool\n")
    
    db_path = 'complaints.db'
    
    # Create backup
    backup_database(db_path)
    
    # Run migration
    migrate_database(db_path)
    
    print("\n🎉 Migration complete! You can now:")
    print("   1. Generate demo data: python demo_data_generator.py")
    print("   2. Start the app: python app.py")
