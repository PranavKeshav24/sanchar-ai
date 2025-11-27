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
    this.theme = theme;
    localStorage.setItem("theme", theme);

    // Update icon
    const icon = document.querySelector(".theme-icon");
    if (icon) {
      icon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
  }

  toggleTheme() {
    const newTheme = this.theme === "light" ? "dark" : "light";
    this.applyTheme(newTheme);
  }

  createThemeSwitcher() {
    const switcher = document.createElement("div");
    switcher.className = "theme-switcher";
    switcher.innerHTML = `
            <button class="theme-toggle" id="themeToggle">
                <span class="theme-icon">${
                  this.theme === "dark" ? "☀️" : "🌙"
                }</span>
                <span>Theme</span>
            </button>
        `;
    document.body.appendChild(switcher);

    document.getElementById("themeToggle").addEventListener("click", () => {
      this.toggleTheme();
    });
  }
}

// Initialize theme manager when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new ThemeManager();
});

// Utility functions for notifications
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `alert alert-${type}`;
  notification.textContent = message;
  notification.style.position = "fixed";
  notification.style.top = "100px";
  notification.style.right = "20px";
  notification.style.zIndex = "10000";
  notification.style.minWidth = "300px";
  notification.style.maxWidth = "500px";

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease-out";
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// Google Maps utility functions
let map;
let markers = [];
let directionsService;
let directionsRenderer;

function initMap(elementId, lat, lng, zoom = 12) {
  const mapOptions = {
    center: { lat: lat, lng: lng },
    zoom: zoom,
    styles: getMapStyles(),
    mapTypeControl: true,
    streetViewControl: true,
    fullscreenControl: true,
    zoomControl: true,
  };

  map = new google.maps.Map(document.getElementById(elementId), mapOptions);
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({
    map: map,
    suppressMarkers: false,
    polylineOptions: {
      strokeColor: "#4f46e5",
      strokeWeight: 5,
    },
  });

  return map;
}

function getMapStyles() {
  const theme = document.documentElement.getAttribute("data-theme");

  if (theme === "dark") {
    return [
      { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
      { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
      { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
      {
        featureType: "administrative.locality",
        elementType: "labels.text.fill",
        stylers: [{ color: "#d59563" }],
      },
      {
        featureType: "poi",
        elementType: "labels.text.fill",
        stylers: [{ color: "#d59563" }],
      },
      {
        featureType: "poi.park",
        elementType: "geometry",
        stylers: [{ color: "#263c3f" }],
      },
      {
        featureType: "poi.park",
        elementType: "labels.text.fill",
        stylers: [{ color: "#6b9a76" }],
      },
      {
        featureType: "road",
        elementType: "geometry",
        stylers: [{ color: "#38414e" }],
      },
      {
        featureType: "road",
        elementType: "geometry.stroke",
        stylers: [{ color: "#212a37" }],
      },
      {
        featureType: "road",
        elementType: "labels.text.fill",
        stylers: [{ color: "#9ca5b3" }],
      },
      {
        featureType: "road.highway",
        elementType: "geometry",
        stylers: [{ color: "#746855" }],
      },
      {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{ color: "#1f2835" }],
      },
      {
        featureType: "road.highway",
        elementType: "labels.text.fill",
        stylers: [{ color: "#f3d19c" }],
      },
      {
        featureType: "transit",
        elementType: "geometry",
        stylers: [{ color: "#2f3948" }],
      },
      {
        featureType: "transit.station",
        elementType: "labels.text.fill",
        stylers: [{ color: "#d59563" }],
      },
      {
        featureType: "water",
        elementType: "geometry",
        stylers: [{ color: "#17263c" }],
      },
      {
        featureType: "water",
        elementType: "labels.text.fill",
        stylers: [{ color: "#515c6d" }],
      },
      {
        featureType: "water",
        elementType: "labels.text.stroke",
        stylers: [{ color: "#17263c" }],
      },
    ];
  }

  return []; // Default light theme
}

function addMarker(lat, lng, title, icon = null, infoContent = null) {
  const markerOptions = {
    position: { lat: lat, lng: lng },
    map: map,
    title: title,
    animation: google.maps.Animation.DROP,
  };

  if (icon) {
    markerOptions.icon = icon;
  }

  const marker = new google.maps.Marker(markerOptions);

  if (infoContent) {
    const infoWindow = new google.maps.InfoWindow({
      content: infoContent,
    });

    marker.addListener("click", () => {
      infoWindow.open(map, marker);
    });
  }

  markers.push(marker);
  return marker;
}

function clearMarkers() {
  markers.forEach((marker) => marker.setMap(null));
  markers = [];
}

function drawRoute(origin, destination, waypoints = []) {
  const request = {
    origin: origin,
    destination: destination,
    waypoints: waypoints,
    travelMode: google.maps.TravelMode.DRIVING,
    drivingOptions: {
      departureTime: new Date(),
      trafficModel: "bestguess",
    },
  };

  directionsService.route(request, (result, status) => {
    if (status === "OK") {
      directionsRenderer.setDirections(result);
    } else {
      console.error("Directions request failed:", status);
      showNotification("Failed to calculate route", "error");
    }
  });
}

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
        }
      );
    } else {
      reject(new Error("Geolocation is not supported"));
    }
  });
}

// Export functions for use in other scripts
window.MapUtils = {
  initMap,
  addMarker,
  clearMarkers,
  drawRoute,
  getCurrentLocation,
  showNotification,
};
