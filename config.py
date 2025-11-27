import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///6g_simulation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or 'YOUR_GOOGLE_MAPS_API_KEY_HERE'
    
    # Default location (can be changed based on deployment)
    DEFAULT_LAT = 12.9716  # Bangalore, India
    DEFAULT_LNG = 77.5946
    
    # Emergency vehicle tracking settings
    EMERGENCY_REFRESH_INTERVAL = 5  # seconds
    ROUTE_UPDATE_THRESHOLD = 100  # meters