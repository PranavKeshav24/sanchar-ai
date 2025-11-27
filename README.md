# Sanchar AI - Smart Traffic Management System

A comprehensive intelligent traffic management system featuring real-time detection, emergency vehicle routing, and AI-powered traffic prediction with Google Maps integration.

## 🚀 Features

### 🗺️ Real-Time Mapping

- **Google Maps Integration**: Interactive maps with traffic, satellite, and terrain views
- **Live Detection Visualization**: Real-time display of pothole and accident detections
- **Geolocation Services**: Precise location tracking with address geocoding
- **Nearby Facilities**: Quick search for hospitals, police stations, and emergency services

### 🚨 Emergency Vehicle Management

- **Real-Time Tracking**: Monitor ambulances, fire trucks, and police vehicles
- **Optimized Routing**: Traffic-aware route calculation with multiple alternatives
- **ETA Prediction**: Accurate arrival time estimates considering current traffic
- **Signal Priority**: Automatic traffic signal management for emergency vehicles
- **Route Alternatives**: Multiple path options with distance and time comparisons

### 🤖 AI-Powered Detection

- **Pothole Detection**: YOLOv5-based real-time identification
- **Accident Detection**: Automatic accident recognition and reporting
- **Live Camera Feed**: Real-time processing from webcam
- **Video Upload**: Batch processing of recorded footage
- **Confidence Scoring**: AI confidence levels for each detection
- **Automatic Complaints**: Geolocation-tagged complaint generation

### 🚦 Traffic Simulation

- **6G V2X Communication**: Vehicle-to-Everything simulation
- **AI Traffic Prediction**: ML-based traffic flow prediction
- **Emergency Priority**: Automatic priority routing for emergency vehicles
- **Multiple Vehicle Types**: Cars, trucks, buses, motorcycles, ambulances
- **Network Slicing**: eMBB, URLLC, and mMTC support

### 🌓 Modern UI/UX

- **Theme Switcher**: Beautiful light and dark themes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-Time Updates**: Live data refresh without page reload
- **Interactive Visualizations**: Dynamic charts and maps
- **Intuitive Navigation**: Easy-to-use interface

## 📋 Prerequisites

- Python 3.8 or higher
- Google Maps API Key
- Webcam (for live detection)
- Modern web browser

## 🔧 Installation

1. **Clone the repository**

```bash
git clone https://github.com/SwathiShreeMB/sanchar-ai.git
cd sanchar-ai
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure Google Maps API**

Create a `.env` file in the root directory:

```env
GOOGLE_MAPS_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

Or update `config.py`:

```python
GOOGLE_MAPS_API_KEY = 'your_api_key_here'
```

**Get Your Google Maps API Key:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Maps JavaScript API
   - Places API
   - Directions API
   - Geocoding API
   - Distance Matrix API
4. Create credentials (API Key)
5. Add restrictions (optional but recommended)

6. **Download YOLOv5 models**

Place your trained models in the `models/` directory:

- `models/ACCIDENT.pt`
- `models/pathole_hump.pt`

## 🚀 Running the Application

1. **Start the Flask server**

```bash
python app.py
```

2. **Access the application**
   Open your browser and navigate to:

```
http://localhost:5000
```

3. **Create an account**

- Register with username, email, and password
- Login to access all features

## 📱 Usage Guide

### Map Dashboard

1. Navigate to "Map View" from the dashboard
2. View all detections as markers on the map
3. Click markers to see detection details
4. Use search to find specific locations
5. Toggle between map views (roadmap, satellite, terrain)

### Emergency Vehicle Tracking

1. Go to "Emergency Tracking"
2. Register a new emergency vehicle:
   - Enter vehicle ID
   - Select type (ambulance, fire truck, police)
   - Set current location and destination
3. View optimized route on map
4. Monitor real-time ETA and progress
5. Complete journey when arrived

### AI Detection

1. Navigate to "AI Detection"
2. Choose detection type (pothole or accident)
3. Options:
   - **Live Detection**: Use webcam for real-time detection
   - **Video Upload**: Upload recorded video for analysis
4. View detection results with confidence scores
5. Automatic complaints filed with geolocation

### Traffic Simulation

1. Go to "Simulation" from dashboard
2. Configure simulation parameters:
   - Number of vehicles per road
   - Enable AI prediction
   - Enable emergency priority
3. Add vehicles to different roads
4. Add ambulances with priority routing
5. Monitor traffic flow and collisions

## 🗺️ Google Maps Features

### Implemented APIs

- **Maps JavaScript API**: Interactive map display
- **Geocoding API**: Convert addresses to coordinates
- **Reverse Geocoding**: Convert coordinates to addresses
- **Directions API**: Calculate routes between points
- **Distance Matrix API**: Get distance/time between locations
- **Places API**: Find nearby hospitals and facilities

### Map Layers

- Roadmap view
- Satellite imagery
- Terrain visualization
- Traffic layer (real-time)
- Street view (future enhancement)

## 🎨 Theme Customization

The application supports light and dark themes:

1. **Theme Switcher**: Located in top-right corner
2. **Automatic Persistence**: Theme preference saved in browser
3. **Map Styling**: Automatically adjusts map colors to match theme

### Custom Theme Colors

Edit `static/css/modern-theme.css`:

```css
:root {
  --accent-primary: #4f46e5; /* Your color */
  --accent-secondary: #7c3aed; /* Your color */
}
```

## 📊 Database Schema

### Users Table

- id, username, email, password_hash, created_at

### Complaints Table

- id, detection_type, confidence, timestamp, location
- description, image_path, latitude, longitude, address

### Emergency Vehicles Table

- id, vehicle_id, vehicle_type, current_lat, current_lng
- destination_lat, destination_lng, status, created_at, updated_at

## 🔒 Security Considerations

1. **API Key Protection**: Never commit API keys to version control
2. **Use Environment Variables**: Store sensitive data in `.env` file
3. **API Restrictions**: Add domain/IP restrictions to Google API key
4. **HTTPS**: Use HTTPS in production
5. **Authentication**: Implement proper user authentication

## 🐛 Troubleshooting

### Google Maps not loading

- Check API key is correct
- Verify APIs are enabled in Google Cloud Console
- Check browser console for errors
- Ensure billing is enabled for Google Cloud project

### Detection not working

- Verify model files exist in `models/` directory
- Check webcam permissions
- Ensure sufficient lighting for detection
- Try adjusting confidence threshold

### Database errors

- Delete `complaints.db` and `6g_simulation.db` to reset
- Run `python app.py` to recreate tables

## 🚀 Future Enhancements

- [ ] Real-time traffic signal integration
- [ ] Mobile application
- [ ] Weather-aware routing
- [ ] Crowd-sourced incident reporting
- [ ] Historical data analytics
- [ ] Predictive maintenance for roads
- [ ] Integration with municipal systems
- [ ] Multi-language support
- [ ] Voice-based alerts
- [ ] Machine learning model improvements

## 📄 API Endpoints

### Map & Location

- `POST /api/geocode` - Convert address to coordinates
- `POST /api/reverse_geocode` - Convert coordinates to address
- `POST /api/route` - Calculate route between points
- `POST /api/nearby_hospitals` - Find nearby hospitals

### Emergency Vehicles

- `POST /api/emergency/register` - Register emergency vehicle
- `POST /api/emergency/update_location` - Update vehicle location
- `GET /api/emergency/status/<vehicle_id>` - Get vehicle status
- `GET /api/emergency/all_active` - Get all active vehicles
- `POST /api/emergency/complete/<vehicle_id>` - Complete journey

### Complaints

- `POST /api/complaints/add_with_location` - Add complaint with geolocation
- `GET /api/complaints/all_with_location` - Get all complaints

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- SwathiShreeMB - Initial work

## 🙏 Acknowledgments

- Google Maps Platform for mapping services
- YOLOv5 by Ultralytics for object detection
- Flask framework for web development
- OpenCV for computer vision capabilities

## 📞 Support

For support, email support@sancharai.com or open an issue in the GitHub repository.

---

Made with ❤️ by the Sanchar AI Team
