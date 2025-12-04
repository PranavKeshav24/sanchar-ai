# Quick Start Guide - Sanchar AI

Get up and running in 5 minutes! ⚡

## Prerequisites

✅ Python 3.8 or higher
✅ Web browser (Chrome recommended)
✅ Internet connection

**No API keys required!** 🎉 We use 100% free and open-source map services.

## Step 1: Get the Code (1 min)

```bash
git clone https://github.com/SwathiShreeMB/sanchar-ai.git
cd sanchar-ai
```

## Step 2: Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

_If you encounter issues, try:_

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 3: Run the Application (30 sec)

No configuration needed! Just run:

```bash
python app.py
```

You should see:

```
* Running on http://127.0.0.1:5000
```

## Step 4: Access the App

Open browser and go to: **http://localhost:5000**

## First Time Setup

### Create Account

1. Click "Register"
2. Enter:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `yourpassword`
3. Click "Register"

### Login

1. Click "Login"
2. Enter your credentials
3. Click "Login"

**You're in! 🎉**

---

## Quick Feature Tour

### 1. Map Dashboard (30 sec)

- Click "Map View"
- **Toggle between 2D and 3D views** using the buttons
- Click "My Location" (allow browser permission)
- Try searching for your city
- Click "Show All Detections"

### 2. 3D Globe Experience 🌍

- Click the "🌍 3D Globe" toggle on any map
- **Drag to rotate** the Earth
- **Scroll to zoom** in/out
- Click "3D Buildings" to see building visualizations
- Toggle between tilted 3D and top-down 2D perspectives

### 3. Emergency Tracking (1 min)

- Click "Emergency Tracking"
- Fill form:
  - Vehicle ID: `AMB-001`
  - Type: `Ambulance`
  - Click "Use My Location" for current
  - Destination: Enter an address
- Click "Start Emergency Route"
- **See the route appear on both 2D and 3D views!**

### 4. AI Detection (Optional - requires webcam)

- Click "AI Detection"
- Click "Live Detection"
- Allow camera access
- Select "Pothole" or "Accident"
- Click "Start Detection"

### 5. Theme Switcher

- Look for button in top-right corner
- Click to toggle Dark/Light mode
- **Maps automatically adapt to theme!**

---

## Map Technology Stack

Sanchar AI uses **100% free and open-source** map technologies:

| Feature      | Technology                  | Why It's Great               |
| ------------ | --------------------------- | ---------------------------- |
| 2D Maps      | **Leaflet + OpenStreetMap** | Fast, reliable, no API key   |
| 3D Globe     | **CesiumJS**                | Google Earth-like experience |
| 3D Buildings | **Cesium OSM Buildings**    | Free 3D building data        |
| Routing      | **OSRM**                    | Open-source directions       |
| Geocoding    | **Nominatim**               | Free address search          |

---

## Common Quick Fixes

### "Map not loading"

**Solution**: Check your internet connection. Maps load from CDN.

### "3D Globe shows blank"

**Solution**:

1. Check browser supports WebGL
2. Try refreshing the page
3. Use 2D map as fallback

### "ImportError: No module named..."

**Solution**:

```bash
pip install -r requirements.txt --force-reinstall
```

### "Camera not working"

**Solution**:

1. Check browser permissions
2. Try different browser
3. Use video upload instead

### "Port 5000 already in use"

**Solution**: Edit `app.py`, last line:

```python
app.run(debug=True, port=5001)  # Use different port
```

---

## Testing Your Setup

### Quick Test Checklist

✅ Homepage loads
✅ Can register/login
✅ Dashboard shows
✅ 2D Map displays
✅ 3D Globe works (toggle button)
✅ Can toggle theme
✅ Emergency form works

If all checked, **you're good to go!**

---

## Next Steps

1. **Explore Features**

   - Try all menu items
   - Toggle between 2D and 3D maps
   - Add some test detections
   - Register emergency vehicles

2. **Customize**

   - Change default location in `config.py`
   - Adjust theme colors in CSS
   - Add your logo

3. **Learn More**
   - Read `README.md` for full documentation
   - Check `CONFIGURATION.md` for customization
   - Review `TESTING_CHECKLIST.md` before deployment

---

## Pro Tips 💡

### Tip 1: Default Location

Change to your city in `config.py`:

```python
DEFAULT_LAT = 40.7128  # New York
DEFAULT_LNG = -74.0060
```

### Tip 2: Theme Colors

Edit `static/css/modern-theme.css`:

```css
:root {
  --accent-primary: #4f46e5; /* Your brand color */
}
```

### Tip 3: 3D Buildings

3D buildings are available in most major cities. Toggle them using the "3D Buildings" button in 3D mode.

### Tip 4: Development

Enable debug mode for better errors:

```python
app.run(debug=True)
```

---

## Keyboard Shortcuts

- `Ctrl + R` - Refresh page
- `F12` - Open browser console (for debugging)
- `Ctrl + Shift + I` - Inspect element
- `Ctrl + 0` - Reset zoom

---

## Need Help?

### Quick Help

1. Check browser console (F12)
2. Check terminal for errors
3. Review `SETUP.md`

### Still Stuck?

- Open an issue on GitHub
- Check existing issues
- Contact: support@sancharai.com

---

## What's Working?

After quick start, you should have:

✅ **Web interface** running
✅ **2D Map (Leaflet)** displaying with OpenStreetMap
✅ **3D Globe (CesiumJS)** with Earth-like visualization
✅ **User authentication** working
✅ **Theme switcher** functional (maps adapt!)
✅ **Emergency routing** via OSRM
✅ **All features** accessible without API keys

---

## Development vs Production

### This Quick Start is for:

- ✅ Development
- ✅ Testing
- ✅ Learning
- ✅ Demos

### For Production, you need:

- ⚠️ Proper server (not flask dev server)
- ⚠️ HTTPS
- ⚠️ Production database
- ⚠️ Security hardening

See `README.md` section on "Production Deployment"

---

## Troubleshooting Commands

```bash
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check if server is running
curl http://localhost:5000

# View running processes (Windows PowerShell)
Get-Process python

# Kill process if needed (Windows)
Stop-Process -Name python
```

---

## Success! 🎉

If you see the dashboard with a working 2D map and can toggle to 3D Globe, **congratulations!** You've successfully set up Sanchar AI.

### What You Can Do Now:

1. Explore all features
2. Toggle between 2D and 3D views
3. Add test data
4. Customize for your needs
5. Contribute improvements

---

**Total Time**: ~3-5 minutes (No API setup needed!)
**Difficulty**: Easy
**Prerequisites**: Basic command line knowledge

---

## Share Your Success!

Got it working? Great! Consider:

- ⭐ Star the repo on GitHub
- 📢 Share with others
- 🐛 Report any issues
- 💡 Suggest improvements
- 🤝 Contribute code

---

**Happy coding! 🚀**

_For detailed documentation, see README.md_
