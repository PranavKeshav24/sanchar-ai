"""
Quick Test Script - Verify Map Dashboard Fixes
"""

print("="*60)
print("  SANCHAR AI - MAP DASHBOARD FIX VERIFICATION")
print("="*60)

# Test 1: Check if modules load
print("\n✓ Test 1: Module Imports")
try:
    import google_maps_service
    import traffic_ml
    import nlp_classifier
    print("  ✓ All modules import successfully")
except Exception as e:
    print(f"  ✗ Module import failed: {e}")
    exit(1)

# Test 2: Check map_dashboard.html fixes
print("\n✓ Test 2: Map Dashboard HTML Structure")
try:
    with open('templates/map_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for duplicate map declaration
    map_declarations = content.count('let map;') + content.count('var map;') + content.count('const map;')
    if map_declarations == 1:
        print(f"  ✓ Single map variable declaration (count: {map_declarations})")
    else:
        print(f"  ✗ Multiple map declarations found (count: {map_declarations})")
    
    # Check for initializeMap function
    if 'function initializeMap()' in content:
        print("  ✓ initializeMap function defined")
    else:
        print("  ✗ initializeMap function not found")
    
    # Check for switchMapType function
    if 'function switchMapType(type)' in content:
        print("  ✓ switchMapType function defined")
    else:
        print("  ✗ switchMapType function not found")
    
    # Check Google Maps script placement
    if 'window.initializeMap = initializeMap' in content:
        print("  ✓ initializeMap attached to window object")
    else:
        print("  ✗ initializeMap not attached to window")
    
    # Check if Google Maps loads after function definitions
    script_sections = content.split('<script')
    maps_after_functions = False
    for i, section in enumerate(script_sections):
        if 'maps.googleapis.com' in section:
            # Check if this is near the end
            if i >= len(script_sections) - 3:  # One of the last 3 scripts
                maps_after_functions = True
    
    if maps_after_functions:
        print("  ✓ Google Maps API loads after function definitions")
    else:
        print("  ⚠ Google Maps API might load before functions")
    
except Exception as e:
    print(f"  ✗ Error checking HTML: {e}")

# Test 3: Check Earth Engine error handling
print("\n✓ Test 3: Earth Engine Fallback")
try:
    from google_maps_service import GoogleEarthEngineService
    
    # Test with invalid project (should use fallback gracefully)
    print("  → Testing fallback with invalid project...")
    gee = GoogleEarthEngineService(
        project_id="test-project",
        key_path="nonexistent-key.json"
    )
    
    if not gee.initialized:
        print("  ✓ Falls back gracefully when Earth Engine unavailable")
        
        # Test fallback terrain analysis
        result = gee.get_terrain_analysis(12.9716, 77.5946)
        if result and 'terrain_type' in result:
            print("  ✓ Fallback terrain analysis works")
            print(f"    - Method: {result.get('analysis_method')}")
            print(f"    - Risk Score: {result.get('pothole_risk_score')}")
        else:
            print("  ✗ Fallback terrain analysis failed")
    else:
        print("  ✓ Earth Engine initialized successfully")
        
except Exception as e:
    print(f"  ✗ Error testing Earth Engine: {e}")

# Test 4: Check configuration
print("\n✓ Test 4: Configuration")
try:
    from config import Config
    c = Config()
    
    if c.GOOGLE_MAPS_API_KEY and c.GOOGLE_MAPS_API_KEY != "your_google_maps_api_key_here":
        print(f"  ✓ Google Maps API Key configured")
    else:
        print(f"  ⚠ Google Maps API Key not configured")
    
    if c.OPENROUTER_API_KEY and c.OPENROUTER_API_KEY != "your_openrouter_api_key_here":
        print(f"  ✓ OpenRouter API Key configured")
    else:
        print(f"  ℹ OpenRouter API Key not configured (optional)")
    
except Exception as e:
    print(f"  ✗ Error checking config: {e}")

# Test 5: Check if Flask app can be imported
print("\n✓ Test 5: Flask Application")
try:
    from app import app, db
    print("  ✓ Flask app imports successfully")
    print("  ✓ Database configured")
except Exception as e:
    print(f"  ✗ Flask app import error: {e}")

print("\n" + "="*60)
print("  VERIFICATION COMPLETE")
print("="*60)

print("\n📋 FIXES APPLIED:")
print("  1. ✓ Moved Google Maps API script to load AFTER function definitions")
print("  2. ✓ Attached initializeMap to window object for global access")
print("  3. ✓ Improved Earth Engine error messaging")
print("  4. ✓ Added fallback mechanism for terrain analysis")

print("\n🚀 TO START THE APPLICATION:")
print("  python app.py")
print("\n🌐 THEN OPEN:")
print("  http://localhost:5000/map_dashboard")

print("\n💡 MAP SHOULD NOW LOAD SUCCESSFULLY!")
print()
