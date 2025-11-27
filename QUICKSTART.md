# Quick Start Guide - Sanchar AI

Get up and running in 5 minutes! ⚡

## Prerequisites

✅ Python 3.8 or higher
✅ Web browser (Chrome recommended)
✅ Internet connection
✅ Google account (for Maps API)

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

## Step 3: Get Google Maps API Key (1 min)

**Quick Method:**

1. Visit: https://console.cloud.google.com/
2. Create new project: "Sanchar-AI"
3. Go to: APIs & Services → Library
4. Enable these (click each):
   - Maps JavaScript API
   - Geocoding API
   - Directions API
   - Places API
5. Go to: APIs & Services → Credentials
6. Create Credentials → API Key
7. **Copy your API key**

## Step 4: Configure API Key (30 sec)

**Option A - Environment Variable (Recommended):**

```bash
# Linux/Mac
export GOOGLE_MAPS_API_KEY='your-api-key-here'

# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY='your-api-key-here'
```

**Option B - Direct Config:**
Edit `config.py`, line 9:

```python
GOOGLE_MAPS_API_KEY = 'your-api-key-here'  # Replace this
```

## Step 5: Run! (30 sec)

```bash
python app.py
```

You should see:

```
* Running on http://127.0.0.1:5000
```

## Step 6: Access the App

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
- Click "My Location" (allow browser permission)
- Try searching for your city
- Click "Show All Detections"

### 2. Emergency Tracking (1 min)

- Click "Emergency Tracking"
- Fill form:
  - Vehicle ID: `AMB-001`
  - Type: `Ambulance`
  - Click "Use My Location" for current
  - Destination: Enter an address
- Click "Register & Start Tracking"
- **See the route appear!**

### 3. AI Detection (Optional - requires webcam)

- Click "AI Detection"
- Click "Live Detection"
- Allow camera access
- Select "Pothole" or "Accident"
- Click "Start Detection"

### 4. Theme Switcher

- Look for button in top-right corner
- Click to toggle Dark/Light mode
- **Instant theme change!**

---

## Common Quick Fixes

### "Map shows 'For development purposes only'"

**Solution**: Enable billing in Google Cloud (don't worry, $200 free/month)

1. Go to: https://console.cloud.google.com/billing
2. Link a billing account (no charges for dev usage)

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

### "API key error"

**Solution**:

1. Check key is correct (no extra spaces)
2. Enable billing in Google Cloud
3. Wait 5 minutes after creating key

---

## Testing Your Setup

### Quick Test Checklist

✅ Homepage loads
✅ Can register/login
✅ Dashboard shows
✅ Map displays
✅ Can toggle theme
✅ Emergency form works

If all checked, **you're good to go!**

---

## Next Steps

1. **Explore Features**

   - Try all menu items
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
  --accent-primary: #4f46e5; /* Your color */
}
```

### Tip 3: API Usage

Monitor at: https://console.cloud.google.com/apis/dashboard

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

## Video Walkthrough

_[Future: Add link to video tutorial]_

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
✅ **Google Maps** displaying
✅ **User authentication** working
✅ **Theme switcher** functional
✅ **Basic features** accessible

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
- ⚠️ API key restrictions
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

# View running processes
ps aux | grep python

# Kill process (if needed)
kill <PID>
```

---

## Success! 🎉

If you see the dashboard with a working map, **congratulations!** You've successfully set up Sanchar AI.

### What You Can Do Now:

1. Explore all features
2. Add test data
3. Customize for your needs
4. Deploy to production
5. Contribute improvements

---

**Total Time**: ~5-10 minutes
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
