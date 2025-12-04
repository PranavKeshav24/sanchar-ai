import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sanchar_ai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys (loaded from .env)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    GOOGLE_EARTH_ENGINE_PROJECT = os.environ.get('GOOGLE_EARTH_ENGINE_PROJECT', '')
    GOOGLE_EARTH_ENGINE_KEY_PATH = os.environ.get('GOOGLE_EARTH_ENGINE_KEY_PATH', 'service-account-key.json')
    
    # Default location (Bangalore, India)
    DEFAULT_LAT = 12.9716
    DEFAULT_LNG = 77.5946
    
    # Emergency vehicle tracking settings
    EMERGENCY_REFRESH_INTERVAL = 5  # seconds
    ROUTE_UPDATE_THRESHOLD = 100  # meters
    
    # 3D Globe settings
    ENABLE_3D_BUILDINGS = True
    ENABLE_TERRAIN = True
    
    # AI/ML Model settings
    YOLO_CONFIDENCE_THRESHOLD = 0.25
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    
    # V2I Communication settings
    V2I_RANGE_METERS = 500
    V2V_RANGE_METERS = 300
    URLLC_LATENCY_THRESHOLD_MS = 10