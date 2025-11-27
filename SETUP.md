# Quick Setup Guide for Sanchar AI

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Google Maps API

### Option A: Using .env file (Recommended)

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Google Maps API key:
   ```
   GOOGLE_MAPS_API_KEY=AIzaSy...your_key_here
   ```

### Option B: Direct configuration

Edit `config.py` and replace:

```python
GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY_HERE'
```

### Getting Your Google Maps API Key

1. **Go to Google Cloud Console**

   - Visit: https://console.cloud.google.com/

2. **Create a Project**

   - Click "Select a project" → "New Project"
   - Name it "Sanchar AI" or similar
   - Click "Create"

3. **Enable Required APIs**
   Navigate to "APIs & Services" → "Library" and enable:

   - ✅ Maps JavaScript API
   - ✅ Places API
   - ✅ Directions API
   - ✅ Geocoding API
   - ✅ Distance Matrix API

4. **Create API Key**

   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

5. **Secure Your API Key (Optional but Recommended)**

   - Click on your API key
   - Under "Application restrictions", select "HTTP referrers"
   - Add: `http://localhost:5000/*`
   - Under "API restrictions", select "Restrict key"
   - Select only the APIs listed above

6. **Enable Billing**
   - Google Maps requires billing to be enabled
   - Don't worry: You get $200 free credit per month
   - For development, you likely won't exceed this

## Step 3: Verify Models

Ensure your trained models are in the `models/` directory:

```
models/
├── ACCIDENT.pt
└── pathole_hump.pt
```

If you don't have models, you can:

- Train your own using YOLOv5
- Use pre-trained models (update paths in app.py)

## Step 4: Initialize Database

The database will be created automatically on first run, but you can initialize manually:

```bash
python -c "from app import db, app; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

## Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Step 6: Create Your First Account

1. Open browser: `http://localhost:5000`
2. Click "Register"
3. Fill in:
   - Username
   - Email
   - Password
4. Click "Register"
5. Login with your credentials

## Step 7: Test Features

### Test Map Dashboard

1. Login → Click "Map View"
2. Should see Google Map centered on default location
3. Click "My Location" to test geolocation
4. Click "Show All Detections" to see markers

### Test Emergency Tracking

1. Click "Emergency Tracking"
2. Fill in form:
   - Vehicle ID: AMB-001
   - Type: Ambulance
   - Current Location: (use "Use My Location")
   - Destination: Enter an address
3. Click "Register & Start Tracking"
4. Route should appear on map with ETA

### Test AI Detection

1. Click "AI Detection" → "Live Detection"
2. Allow camera access
3. Select detection type (pothole/accident)
4. Click "Start Detection"
5. Point camera at road scenes

## Troubleshooting

### Maps not loading

**Error**: Blank map or "For development purposes only" watermark
**Solution**:

- Check API key is correct
- Verify APIs are enabled
- Enable billing on Google Cloud

### Camera not working

**Error**: "Camera access denied"
**Solution**:

- Allow camera permissions in browser
- Check if another app is using camera
- Try different browser

### Import errors

**Error**: `ModuleNotFoundError`
**Solution**:

```bash
pip install -r requirements.txt --upgrade
```

### Database errors

**Error**: Table doesn't exist
**Solution**:

```bash
# Delete old databases
rm *.db
# Restart application
python app.py
```

### Port already in use

**Error**: `Address already in use`
**Solution**:

```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or change port in app.py:
app.run(debug=True, port=5001)
```

## Common Issues

### Issue: Maps show but no route appears

**Cause**: Directions API not enabled or invalid addresses
**Fix**:

1. Enable Directions API in Google Cloud Console
2. Use full addresses like "123 Main St, City, State"
3. Check browser console for errors

### Issue: Detections not saved

**Cause**: Database write permissions
**Fix**:

```bash
chmod 666 complaints.db  # Mac/Linux
# On Windows, check file isn't read-only
```

### Issue: High API usage/costs

**Cause**: Too many API calls
**Fix**:

1. Set API quotas in Google Cloud Console
2. Implement caching for geocoding results
3. Reduce refresh intervals

## Performance Optimization

### For Faster Detection

1. Use smaller input resolution
2. Adjust confidence threshold
3. Process fewer frames per second

### For Better Maps Performance

1. Reduce marker count on map
2. Cluster nearby markers
3. Use map tile caching

## Next Steps

1. Customize default location in `config.py`
2. Train models on your local road data
3. Add more emergency vehicle types
4. Customize UI theme colors
5. Deploy to production server

## Getting Help

- Check README.md for detailed documentation
- Review app.py for API endpoints
- Check browser console for JavaScript errors
- Check terminal for Python errors

## Production Deployment

When deploying to production:

1. **Set Environment Variables**

   ```bash
   export GOOGLE_MAPS_API_KEY=your_key
   export SECRET_KEY=random_secret_key
   export FLASK_ENV=production
   ```

2. **Use Production Server**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Setup HTTPS**

   - Use nginx as reverse proxy
   - Get SSL certificate (Let's Encrypt)

4. **Restrict API Key**

   - Add production domain to API restrictions
   - Set up billing alerts

5. **Database**
   - Use PostgreSQL instead of SQLite
   - Set up regular backups

---

Happy Coding! 🚀
