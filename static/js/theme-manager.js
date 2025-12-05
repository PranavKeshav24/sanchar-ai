/**
 * Sanchar AI - Theme Manager & Map Utilities
 * Using CesiumJS for 3D Globe Visualization (Google Earth-like)
 * Free and Open Source with Leaflet + OpenStreetMap fallback
 */

console.log("Theme Manager script loading..."); // Logging script loading

// Global map state
var currentMapType = "leaflet"; // 'cesium' or 'leaflet'
var leafletMap = null;
var leafletMarkers = [];
var leafletRouteLayer = null;

// Theme Switcher
class ThemeManager {
  constructor() {
    this.theme = localStorage.getItem("theme") || "light";
    this.init();
  }

  init() {
    this.applyTheme(this.theme);
    this.createThemeSwitcher();
  }

  applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.body.setAttribute("data-theme", theme);
    this.theme = theme;
    localStorage.setItem("theme", theme);

    // Update all elements with theme class
    document
      .querySelectorAll(".card, .navbar, .btn, .form-control, table, .alert")
      .forEach((el) => {
        el.style.transition = "all 0.3s ease";
      });

    // Update icon
    const icon = document.querySelector(".theme-icon");
    if (icon) {
      icon.textContent = theme === "dark" ? "☀️" : "🌙";
    }

    // Update Cesium viewer style if it exists
    if (window.cesiumViewer) {
      updateCesiumTheme(theme);
    }

    // Update Leaflet map if it exists
    if (leafletMap) {
      updateLeafletTheme(theme);
    }

    // Broadcast theme change event
    window.dispatchEvent(new CustomEvent("themechange", { detail: { theme } }));
  }

  toggleTheme() {
    const newTheme = this.theme === "light" ? "dark" : "light";
    this.applyTheme(newTheme);
    showNotification(`Switched to ${newTheme} mode`, "success");
  }

  createThemeSwitcher() {
    // Remove existing switcher if any
    const existing = document.querySelector(".theme-switcher");
    if (existing) existing.remove();

    const switcher = document.createElement("div");
    switcher.className = "theme-switcher";
    switcher.innerHTML = `
      <button class="theme-toggle" id="themeToggle" title="Toggle theme">
        <span class="theme-icon">${this.theme === "dark" ? "☀️" : "🌙"}</span>
        <span class="theme-label">${
          this.theme === "dark" ? "Light" : "Dark"
        }</span>
      </button>
    `;
    document.body.appendChild(switcher);

    document.getElementById("themeToggle").addEventListener("click", () => {
      this.toggleTheme();
      // Update label
      const label = document.querySelector(".theme-label");
      if (label) {
        label.textContent = this.theme === "dark" ? "Light" : "Dark";
      }
    });
  }
}

// Initialize theme manager when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.themeManager = new ThemeManager();

  // Move theme switcher to navbar if it exists
  const navbar = document.querySelector(".navbar-nav");
  const switcher = document.querySelector(".theme-switcher");

  if (navbar && switcher) {
    const li = document.createElement("li");
    li.className = "nav-item ms-2";

    // Extract the button from the fixed container
    const btn = switcher.querySelector(".theme-toggle");
    if (btn) {
      btn.classList.add("nav-link", "btn", "btn-link");
      btn.style.background = "transparent";
      btn.style.border = "none";
      btn.style.boxShadow = "none";

      li.appendChild(btn);
      navbar.appendChild(li);

      // Remove the fixed container
      switcher.remove();
    }
  }
});

// Utility functions for notifications
function showNotification(message, type = "info") {
  // Remove any existing notifications of same type
  const existing = document.querySelectorAll(".notification-toast");
  existing.forEach((n) => {
    if (n.dataset.type === type) n.remove();
  });

  const notification = document.createElement("div");
  notification.className = `notification-toast alert alert-${type}`;
  notification.dataset.type = type;
  notification.innerHTML = `
    <span class="notification-icon">${getNotificationIcon(type)}</span>
    <span class="notification-message">${message}</span>
    <button class="notification-close" onclick="this.parentElement.remove()">×</button>
  `;
  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 10000;
    min-width: 300px;
    max-width: 450px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    animation: slideInRight 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    backdrop-filter: blur(10px);
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOutRight 0.3s ease-out forwards";
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 300);
  }, 4000);
}

function getNotificationIcon(type) {
  const icons = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️",
  };
  return icons[type] || icons.info;
}

// ============================================
// Leaflet Map (Primary - More Reliable)
// ============================================

/**
 * Initialize Leaflet Map (Primary map provider)
 */
function initLeafletMap(elementId, lat, lng, zoom = 13) {
  const container = document.getElementById(elementId);
  if (!container) {
    console.error(`Element with id '${elementId}' not found`);
    return null;
  }

  // Show loading state
  container.innerHTML =
    '<div class="map-loading"><div class="spinner"></div><p>Loading interactive map...</p></div>';

  try {
    // Clear container
    container.innerHTML = "";

    // Initialize Leaflet map
    leafletMap = L.map(elementId, {
      center: [lat, lng],
      zoom: zoom,
      zoomControl: true,
      attributionControl: true,
    });

    // Add tile layer based on theme
    const theme = document.documentElement.getAttribute("data-theme");
    updateLeafletTheme(theme);

    // Store globally
    window.leafletMap = leafletMap;
    currentMapType = "leaflet";

    console.log("Leaflet map initialized successfully");
    return leafletMap;
  } catch (error) {
    console.error("Failed to initialize Leaflet map:", error);
    container.innerHTML = `
      <div class="map-error">
        <p>⚠️ Map failed to load</p>
        <button onclick="initLeafletMap('${elementId}', ${lat}, ${lng}, ${zoom})" class="btn btn-primary">Retry</button>
      </div>
    `;
    return null;
  }
}

/**
 * Update Leaflet map theme
 */
function updateLeafletTheme(theme) {
  if (!leafletMap) return;

  // Remove existing tile layers
  leafletMap.eachLayer((layer) => {
    if (layer instanceof L.TileLayer) {
      leafletMap.removeLayer(layer);
    }
  });

  // Add appropriate tile layer
  if (theme === "dark") {
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: "abcd",
        maxZoom: 20,
      }
    ).addTo(leafletMap);
  } else {
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(leafletMap);
  }
}

// ============================================
// CesiumJS 3D Globe Utilities (Google Earth-like)
// ============================================

var cesiumViewer = null;
var cesiumEntities = [];
var routeEntities = [];

/**
 * Initialize Cesium 3D Globe Viewer
 * Uses FREE open-source data: Cesium World Terrain + Bing/ESRI Imagery + OSM Buildings
 * Provides a Google Earth-like experience without requiring paid APIs
 */
async function initCesiumMap(elementId, lat, lng, zoom = 12, apiKey = null) {
  // Check if Cesium is available
  if (typeof Cesium === "undefined") {
    console.error("CesiumJS library not loaded. Please check script tags.");
    throw new Error("CesiumJS not loaded");
  }

  const container = document.getElementById(elementId);
  if (!container) {
    console.error(`Element with id '${elementId}' not found`);
    return null;
  }

  // Show loading state
  container.innerHTML =
    '<div class="map-loading" style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Loading 3D Globe...</p></div>';

  try {
    // Clear container
    container.innerHTML = "";

    // Use FREE OpenStreetMap imagery - NO authentication required!
    cesiumViewer = new Cesium.Viewer(elementId, {
      baseLayerPicker: false, // Disable to avoid Ion dependency
      geocoder: false,
      homeButton: true,
      sceneModePicker: true,
      navigationHelpButton: false,
      animation: false,
      timeline: false,
      fullscreenButton: true,
      vrButton: false,
      selectionIndicator: true,
      infoBox: true,
      shadows: true,
      sceneMode: Cesium.SceneMode.SCENE3D,
      // Use OpenStreetMap imagery (completely free, no authentication)
      imageryProvider: new Cesium.OpenStreetMapImageryProvider({
        url: "https://a.tile.openstreetmap.org/",
      }),
      // Use basic ellipsoid terrain (no authentication needed)
      terrainProvider: new Cesium.EllipsoidTerrainProvider(),
    });

    // Hide default credits container (we'll add attribution elsewhere if needed)
    cesiumViewer.cesiumWidget.creditContainer.style.display = "none";

    // Enable realistic rendering for Google Earth-like experience
    cesiumViewer.scene.globe.enableLighting = true; // IMPORTANT: Enables sun lighting
    cesiumViewer.scene.skyAtmosphere.show = true;
    cesiumViewer.scene.fog.enabled = true;
    cesiumViewer.scene.globe.showGroundAtmosphere = true;

    // Enable depth testing for better 3D effect
    cesiumViewer.scene.globe.depthTestAgainstTerrain = true;

    // Set high quality rendering
    cesiumViewer.scene.highDynamicRange = true;
    cesiumViewer.scene.requestRenderMode = false; // Always render for smooth experience

    // Set time to current time for realistic sun position
    const currentTime = Cesium.JulianDate.now();
    cesiumViewer.clock.currentTime = currentTime;
    cesiumViewer.clock.shouldAnimate = false;

    // Store globally
    window.cesiumViewer = cesiumViewer;
    currentMapType = "cesium";

    // Fly to initial location IMMEDIATELY
    flyToLocation(lat, lng, zoom);

    // Add OSM 3D Buildings for city details
    try {
      const osmBuildings = await Cesium.createOsmBuildingsAsync();
      if (cesiumViewer) {
        cesiumViewer.scene.primitives.add(osmBuildings);
        console.log("✅ 3D Buildings loaded successfully");
      }
    } catch (buildingError) {
      console.warn("Could not load OSM Buildings:", buildingError);
      // Continue without buildings - not critical
    }

    // Apply theme
    const theme = document.documentElement.getAttribute("data-theme");
    updateCesiumTheme(theme);

    console.log("Cesium 3D globe initialized successfully");
    return cesiumViewer;
  } catch (error) {
    console.error("Failed to initialize Cesium Globe:", error);
    // Cleanup
    if (cesiumViewer) {
      cesiumViewer.destroy();
      cesiumViewer = null;
    }
    container.innerHTML = `
      <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted p-4">
        <i class="fas fa-exclamation-triangle fa-3x mb-3 text-warning"></i>
        <h5>3D Globe Failed to Load</h5>
        <p class="text-center small">${
          error && error.message ? error.message : String(error)
        }</p>
        <button class="btn btn-primary mt-3" onclick="location.reload()">Reload Page</button>
      </div>
    `;
    throw error;
  }
}

/**
 * Initialize map with automatic fallback
 */
function initMap(elementId, lat, lng, zoom = 12) {
  // Try Cesium first if available, otherwise use Leaflet
  if (typeof Cesium !== "undefined") {
    return initCesiumMap(elementId, lat, lng, zoom);
  } else if (typeof L !== "undefined") {
    return initLeafletMap(elementId, lat, lng, zoom);
  } else {
    console.error("No map library available");
    const container = document.getElementById(elementId);
    if (container) {
      container.innerHTML = `
        <div class="map-error" style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:var(--bg-secondary);border-radius:12px;">
          <p style="font-size:3rem;margin-bottom:1rem;">🗺️</p>
          <p style="color:var(--text-secondary);">Map library not loaded</p>
        </div>
      `;
    }
    return null;
  }
}

/**
 * Update Cesium viewer theme
 */
function updateCesiumTheme(theme) {
  if (!cesiumViewer) return;

  // Keep lighting enabled for realistic globe (not a blue sphere!)
  cesiumViewer.scene.globe.enableLighting = true;

  if (theme === "dark") {
    // Dark theme - night mode
    cesiumViewer.scene.skyAtmosphere.show = true;
    cesiumViewer.scene.fog.enabled = true;
  } else {
    // Light theme - day mode
    cesiumViewer.scene.skyAtmosphere.show = true;
    cesiumViewer.scene.fog.enabled = false;
  }
}

/**
 * Fly to a specific location with smooth animation
 */
function flyToLocation(lat, lng, zoom = 15) {
  // Use Leaflet if active
  if (currentMapType === "leaflet" && leafletMap) {
    leafletMap.flyTo([lat, lng], zoom, { duration: 1.5 });
    return;
  }

  // Use Cesium if active
  if (currentMapType === "cesium" && cesiumViewer) {
    const altitude = zoomToAltitude(zoom);
    cesiumViewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(lng, lat, altitude),
      orientation: {
        heading: Cesium.Math.toRadians(0),
        pitch: Cesium.Math.toRadians(-45),
        roll: 0,
      },
      duration: 2.0,
    });
  }
}

/**
 * Convert Google Maps-style zoom to altitude in meters
 */
function zoomToAltitude(zoom) {
  // Approximate conversion
  const altitudes = {
    1: 20000000,
    5: 5000000,
    8: 500000,
    10: 100000,
    12: 30000,
    13: 15000,
    14: 8000,
    15: 4000,
    16: 2000,
    17: 1000,
    18: 500,
    19: 250,
    20: 125,
  };
  return altitudes[Math.min(Math.max(zoom, 1), 20)] || 15000;
}

/**
 * Add a marker to the map (works with both Leaflet and Cesium)
 */
function addMarker(lat, lng, title, icon = null, infoContent = null) {
  // Use Leaflet if available
  if (currentMapType === "leaflet" && leafletMap) {
    return addLeafletMarker(lat, lng, title, icon, infoContent);
  }
  // Use Cesium if available
  if (currentMapType === "cesium" && cesiumViewer) {
    return addCesiumMarker(lat, lng, title, icon, infoContent);
  }
  console.warn("No map initialized for adding marker");
  return null;
}

/**
 * Add a Leaflet marker
 */
function addLeafletMarker(lat, lng, title, icon = null, infoContent = null) {
  if (!leafletMap) return null;

  // Determine marker color based on title
  let markerColor = "#4f46e5";
  let emoji = "📍";

  if (title && title.toLowerCase().includes("pothole")) {
    markerColor = "#f59e0b";
    emoji = "🕳️";
  } else if (title && title.toLowerCase().includes("accident")) {
    markerColor = "#ef4444";
    emoji = "🚨";
  } else if (title && title.toLowerCase().includes("hospital")) {
    markerColor = "#10b981";
    emoji = "🏥";
  } else if (title && title.toLowerCase().includes("ambulance")) {
    markerColor = "#ef4444";
    emoji = "🚑";
  } else if (title && title.toLowerCase().includes("fire")) {
    markerColor = "#f97316";
    emoji = "🚒";
  } else if (title && title.toLowerCase().includes("police")) {
    markerColor = "#3b82f6";
    emoji = "🚓";
  } else if (title && title.toLowerCase().includes("location")) {
    emoji = "📍";
  }

  // Create custom icon
  const customIcon = L.divIcon({
    html: `<div style="
      background: ${markerColor};
      width: 36px;
      height: 36px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      border: 3px solid white;
    "><span style="transform: rotate(45deg); font-size: 16px;">${emoji}</span></div>`,
    className: "custom-marker",
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36],
  });

  const marker = L.marker([lat, lng], { icon: customIcon }).addTo(leafletMap);

  if (infoContent || title) {
    marker.bindPopup(`
      <div style="min-width: 200px; padding: 8px;">
        <h4 style="margin: 0 0 8px 0; color: #333;">${title}</h4>
        ${infoContent || ""}
      </div>
    `);
  }

  leafletMarkers.push(marker);
  return marker;
}

/**
 * Add a 3D marker/billboard to the Cesium globe
 */
function addCesiumMarker(lat, lng, title, icon = null, infoContent = null) {
  if (!cesiumViewer) return null;

  // Determine marker color based on type
  let markerColor = Cesium.Color.BLUE;
  let markerImage = null;

  if (icon) {
    if (typeof icon === "object" && icon.url) {
      markerImage = icon.url;
    } else if (typeof icon === "string") {
      markerImage = icon;
    }
  }

  // Infer color from title or marker image
  if (title && title.toLowerCase().includes("pothole")) {
    markerColor = Cesium.Color.YELLOW;
  } else if (title && title.toLowerCase().includes("accident")) {
    markerColor = Cesium.Color.RED;
  } else if (title && title.toLowerCase().includes("hospital")) {
    markerColor = Cesium.Color.GREEN;
  } else if (title && title.toLowerCase().includes("ambulance")) {
    markerColor = Cesium.Color.RED;
  } else if (title && title.toLowerCase().includes("fire")) {
    markerColor = Cesium.Color.ORANGE;
  } else if (title && title.toLowerCase().includes("police")) {
    markerColor = Cesium.Color.BLUE;
  }

  const entity = cesiumViewer.entities.add({
    position: Cesium.Cartesian3.fromDegrees(lng, lat, 10),
    name: title,
    description: infoContent || title,
    point: markerImage
      ? undefined
      : {
          pixelSize: 15,
          color: markerColor,
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 3,
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
    billboard: markerImage
      ? {
          image: markerImage,
          width: 40,
          height: 40,
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        }
      : undefined,
    label: {
      text: title,
      font: "14px sans-serif",
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      pixelOffset: new Cesium.Cartesian2(0, -50),
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
      showBackground: true,
      backgroundColor: new Cesium.Color(0, 0, 0, 0.7),
    },
  });

  cesiumEntities.push(entity);
  return entity;
}

/**
 * Clear all markers from the map
 */
function clearMarkers() {
  // Clear Leaflet markers
  if (leafletMap) {
    leafletMarkers.forEach((marker) => {
      leafletMap.removeLayer(marker);
    });
    leafletMarkers = [];
  }

  // Clear Cesium markers
  if (cesiumViewer) {
    cesiumEntities.forEach((entity) => {
      cesiumViewer.entities.remove(entity);
    });
    cesiumEntities = [];
  }
}

/**
 * Draw a route on the map
 */
function drawRoute(origin, destination, waypoints = [], routeData = null) {
  if (currentMapType === "leaflet" && leafletMap) {
    return drawLeafletRoute(origin, destination, waypoints, routeData);
  }
  if (currentMapType === "cesium" && cesiumViewer) {
    return drawCesiumRoute(origin, destination, waypoints, routeData);
  }
  return null;
}

/**
 * Draw route on Leaflet map
 */
function drawLeafletRoute(
  origin,
  destination,
  waypoints = [],
  routeData = null
) {
  if (!leafletMap) return null;

  // Clear existing route
  clearRoutes();

  if (routeData && routeData.polyline && routeData.polyline.length > 0) {
    const latlngs = routeData.polyline.map((point) => [point.lat, point.lng]);

    leafletRouteLayer = L.polyline(latlngs, {
      color: "#4f46e5",
      weight: 6,
      opacity: 0.8,
      lineJoin: "round",
      lineCap: "round",
    }).addTo(leafletMap);

    // Add glow effect
    L.polyline(latlngs, {
      color: "#818cf8",
      weight: 10,
      opacity: 0.3,
    }).addTo(leafletMap);

    // Fit bounds
    leafletMap.fitBounds(leafletRouteLayer.getBounds(), { padding: [50, 50] });

    // Add start/end markers
    const startPoint = routeData.polyline[0];
    const endPoint = routeData.polyline[routeData.polyline.length - 1];

    addMarker(
      startPoint.lat,
      startPoint.lng,
      "Start",
      null,
      `<strong>Start:</strong> ${routeData.start_address || "Origin"}`
    );
    addMarker(
      endPoint.lat,
      endPoint.lng,
      "Destination",
      null,
      `
      <strong>Destination:</strong> ${
        routeData.end_address || "Destination"
      }<br>
      <strong>Distance:</strong> ${routeData.distance}<br>
      <strong>Duration:</strong> ${routeData.duration}
    `
    );

    return leafletRouteLayer;
  }

  return null;
}

/**
 * Draw a 3D route on the Cesium globe
 */
function drawCesiumRoute(
  origin,
  destination,
  waypoints = [],
  routeData = null
) {
  if (!cesiumViewer) return null;

  // Clear existing routes
  clearRoutes();

  if (routeData && routeData.polyline && routeData.polyline.length > 0) {
    const positions = routeData.polyline.map((point) =>
      Cesium.Cartesian3.fromDegrees(point.lng, point.lat, 50)
    );

    const routeEntity = cesiumViewer.entities.add({
      name: "Route",
      polyline: {
        positions: positions,
        width: 8,
        material: new Cesium.PolylineGlowMaterialProperty({
          glowPower: 0.3,
          color: Cesium.Color.fromCssColorString("#4f46e5"),
        }),
        clampToGround: true,
      },
    });

    routeEntities.push(routeEntity);

    // Add start marker
    const startEntity = addCesiumMarker(
      routeData.polyline[0].lat,
      routeData.polyline[0].lng,
      "Start",
      null,
      `<strong>Start:</strong> ${routeData.start_address || "Origin"}`
    );
    routeEntities.push(startEntity);

    // Add end marker
    const endPoint = routeData.polyline[routeData.polyline.length - 1];
    const endEntity = addCesiumMarker(
      endPoint.lat,
      endPoint.lng,
      "Destination",
      null,
      `<strong>Destination:</strong> ${
        routeData.end_address || "Destination"
      }<br>
       <strong>Distance:</strong> ${routeData.distance}<br>
       <strong>Duration:</strong> ${routeData.duration}`
    );
    routeEntities.push(endEntity);

    // Fly to show entire route
    cesiumViewer.flyTo(routeEntity, {
      duration: 2.0,
      offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-45), 0),
    });

    return routeEntity;
  }

  return null;
}

/**
 * Clear all routes from the map
 */
function clearRoutes() {
  // Clear Leaflet route
  if (leafletMap && leafletRouteLayer) {
    leafletMap.removeLayer(leafletRouteLayer);
    leafletRouteLayer = null;
  }

  // Clear Cesium routes
  if (cesiumViewer) {
    routeEntities.forEach((entity) => {
      cesiumViewer.entities.remove(entity);
    });
    routeEntities = [];
  }
}

/**
 * Get current device location
 */
function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    } else {
      reject(new Error("Geolocation is not supported"));
    }
  });
}

/**
 * Set camera to look straight down (2D-like view)
 */
function setTopDownView(lat, lng, altitude = 5000) {
  if (!cesiumViewer) return;

  cesiumViewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(lng, lat, altitude),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(-90), // Look straight down
      roll: 0,
    },
    duration: 1.5,
  });
}

/**
 * Set camera to 3D perspective view
 */
function set3DView(lat, lng, altitude = 5000) {
  if (!cesiumViewer) return;

  cesiumViewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(lng, lat, altitude),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0,
    },
    duration: 1.5,
  });
}

/**
 * Toggle between 2D and 3D modes
 */
function toggleViewMode() {
  if (!cesiumViewer) return;

  const currentMode = cesiumViewer.scene.mode;

  if (currentMode === Cesium.SceneMode.SCENE3D) {
    cesiumViewer.scene.morphTo2D(1.5);
  } else {
    cesiumViewer.scene.morphTo3D(1.5);
  }
}

/**
 * Add 3D building visualization (where available)
 * Note: Buildings are now loaded automatically in initCesiumMap
 */
async function add3DBuildings() {
  if (!cesiumViewer) return;

  // Buildings are already loaded during initialization
  // This function is kept for backward compatibility
  console.log("3D Buildings already loaded during initialization");
}

/**
 * Screenshot the current view
 */
function captureScreenshot() {
  if (!cesiumViewer) return null;

  cesiumViewer.render();
  return cesiumViewer.canvas.toDataURL("image/png");
}

// ============================================
// Compatibility layer for existing code
// These functions maintain compatibility with
// code that was written for Google Maps
// ============================================

// Map object compatibility
const map = {
  setCenter: function (location) {
    if (location.lat && location.lng) {
      flyToLocation(location.lat, location.lng, 15);
    }
  },
  setZoom: function (zoom) {
    if (cesiumViewer) {
      const cameraPosition = cesiumViewer.camera.positionCartographic;
      const altitude = zoomToAltitude(zoom);
      cesiumViewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromRadians(
          cameraPosition.longitude,
          cameraPosition.latitude,
          altitude
        ),
        duration: 1.0,
      });
    }
  },
  fitBounds: function (bounds) {
    // Cesium equivalent
    if (cesiumViewer && bounds) {
      cesiumViewer.camera.flyTo({
        destination: Cesium.Rectangle.fromDegrees(
          bounds.west,
          bounds.south,
          bounds.east,
          bounds.north
        ),
        duration: 2.0,
      });
    }
  },
};

// Export functions for use in other scripts
window.MapUtils = {
  // Core functions
  initMap,
  initLeafletMap,
  initCesiumMap,
  addMarker,
  clearMarkers,
  drawRoute,
  clearRoutes,
  getCurrentLocation,
  showNotification,

  // 3D specific functions
  flyToLocation,
  setTopDownView,
  set3DView,
  toggleViewMode,
  add3DBuildings,
  captureScreenshot,

  // Theme
  updateCesiumTheme,
  updateLeafletTheme,

  // Compatibility
  map,
};

// Also expose initLeafletMap globally for direct access
window.initLeafletMap = initLeafletMap;
window.initCesiumMap = initCesiumMap;
