# Configuration Guide

## Application Settings

### Default Location

The application uses Bangalore, India as the default location. To change this:

Edit `config.py`:

```python
DEFAULT_LAT = 40.7128  # New York
DEFAULT_LNG = -74.0060
```

Or use environment variables:

```bash
export DEFAULT_LAT=40.7128
export DEFAULT_LNG=-74.0060
```

### Emergency Vehicle Settings

**Refresh Interval**: How often to update vehicle positions (seconds)

```python
EMERGENCY_REFRESH_INTERVAL = 5  # Update every 5 seconds
```

**Route Update Threshold**: Distance in meters before recalculating route

```python
ROUTE_UPDATE_THRESHOLD = 100  # Recalculate if 100m off route
```

## Google Maps Configuration

### API Key Setup

1. **Development Environment**

   ```python
   # config.py
   GOOGLE_MAPS_API_KEY = 'AIzaSy...development_key'
   ```

2. **Production Environment**
   ```bash
   # .env file
   GOOGLE_MAPS_API_KEY=AIzaSy...production_key
   ```

### Map Customization

#### Default Zoom Level

Edit templates to change default zoom:

```javascript
// In map_dashboard.html
map = MapUtils.initMap("map", DEFAULT_LAT, DEFAULT_LNG, 13); // 13 = zoom level
```

Zoom levels:

- 1-3: World
- 4-6: Landmass/continent
- 7-10: City
- 11-14: District
- 15-17: Streets
- 18-20: Buildings

#### Map Type

Available types:

- `roadmap`: Default road map
- `satellite`: Satellite imagery
- `terrain`: Terrain features
- `hybrid`: Satellite + road labels

```javascript
const mapOptions = {
  center: { lat: lat, lng: lng },
  zoom: zoom,
  mapTypeId: "satellite", // Change here
};
```

## Detection Configuration

### Confidence Threshold

Adjust detection sensitivity:

```python
# app.py - get_model function
model.conf = 0.25  # Lower = more detections, higher = more accurate
```

Recommended values:

- 0.15-0.25: High sensitivity (more false positives)
- 0.25-0.50: Balanced
- 0.50-0.75: High precision (may miss some)

### Video Processing

**Frame Processing Rate**

```python
# app.py - generate_processed_frames
time.sleep(0.03)  # Process ~30 FPS, adjust for performance
```

**Video Resolution**

```python
# app.py - resize_frame
frame = resize_frame(frame, max_width=800)  # Adjust resolution
```

## Theme Configuration

### Custom Colors

Edit `static/css/modern-theme.css`:

```css
:root {
  /* Light Theme */
  --accent-primary: #4f46e5; /* Primary color */
  --accent-secondary: #7c3aed; /* Secondary color */
  --accent-success: #10b981; /* Success messages */
  --accent-warning: #f59e0b; /* Warnings */
  --accent-danger: #ef4444; /* Errors/alerts */
}
```

### Dark Theme Colors

```css
[data-theme="dark"] {
  --bg-primary: #1a1a2e; /* Main background */
  --bg-secondary: #16213e; /* Secondary background */
  --text-primary: #e4e4e7; /* Primary text */
}
```

## Database Configuration

### SQLite (Default)

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///6g_simulation.db'
```

### PostgreSQL (Production)

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/sanchar_ai'
```

### MySQL

```python
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/sanchar_ai'
```

## Upload Configuration

### File Size Limit

```python
# app.py
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

### Allowed File Types

```python
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'mkv', 'flv'}
```

## Performance Tuning

### Map Marker Limits

To prevent slowdowns with many markers:

```javascript
// map_dashboard.html
if (data.complaints.length > 500) {
  // Implement clustering or pagination
}
```

### Database Optimization

```python
# Add indexes for better performance
CREATE INDEX idx_complaints_lat_lng ON complaints(latitude, longitude);
CREATE INDEX idx_complaints_type ON complaints(detection_type);
```

### Caching Geocoding Results

```python
# Implement caching to reduce API calls
from functools import lru_cache

@lru_cache(maxsize=1000)
def geocode_cached(address):
    return maps_service.geocode_address(address)
```

## Security Configuration

### Session Configuration

```python
# config.py
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
```

### API Key Restrictions

**HTTP Referrer Restrictions**

```
http://localhost:5000/*
https://yourdomain.com/*
```

**IP Address Restrictions**

```
123.456.789.0  # Your server IP
```

### CORS Configuration

```python
from flask_cors import CORS

# Allow specific origins
CORS(app, resources={
    r"/api/*": {"origins": ["https://yourdomain.com"]}
})
```

## Email Configuration (Optional)

For sending alerts:

```python
# config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
```

## Logging Configuration

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Environment-Specific Configs

### Development

```python
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries
```

### Production

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    # Use production API keys
```

### Testing

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

## Backup Configuration

### Database Backup

```bash
# SQLite backup
sqlite3 complaints.db .dump > backup.sql

# Restore
sqlite3 new_database.db < backup.sql
```

### Automated Backups

```bash
# Add to crontab for daily backups
0 2 * * * sqlite3 /path/to/complaints.db .dump > /backups/complaints_$(date +\%Y\%m\%d).sql
```

## Monitoring Configuration

### Enable Flask-DebugToolbar (Development)

```python
from flask_debugtoolbar import DebugToolbarExtension

app.config['DEBUG_TB_ENABLED'] = True
toolbar = DebugToolbarExtension(app)
```

### Application Monitoring (Production)

```python
# Example with Sentry
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

## Custom Map Styles

### Use Custom Map Style

```javascript
// Create custom style at https://mapstyle.withgoogle.com/
const customMapStyle = [
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#38414e" }],
  },
  // ... more styles
];

const mapOptions = {
  styles: customMapStyle,
};
```

## API Rate Limiting

### Implement rate limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/route')
@limiter.limit("10 per minute")
def get_route():
    # Your route logic
```

---

For more information, see README.md and SETUP.md
