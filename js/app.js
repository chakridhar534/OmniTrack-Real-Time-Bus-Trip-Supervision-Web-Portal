/* ============================================
   OmniTrack — Shared Application JavaScript
   ============================================ */

const API_BASE = (window.location.protocol.startsWith('http') && window.location.port === '8000')
  ? window.location.origin
  : 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initPasswordToggle();
  initRoleToggle();
  initBusStopFilter();
  initFormValidation();
  initFormSubmit();
  initDashboard();
  initForgotPassword();
});

/* --- Navbar Scroll Effect & Mobile Toggle --- */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  const toggle = document.querySelector('.navbar__toggle');
  const links = document.querySelector('.navbar__links');

  // Scroll effect
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    });
  }

  // Mobile toggle
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('active');
      toggle.classList.toggle('open');
    });

    // Close menu on link click
    links.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        links.classList.remove('active');
        toggle.classList.remove('open');
      });
    });
  }
}

/* --- Password Visibility Toggle --- */
function initPasswordToggle() {
  const toggleBtns = document.querySelectorAll('.password-toggle');

  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const wrapper = btn.closest('.password-wrapper');
      const input = wrapper.querySelector('.form-input');
      const eyeOpen = btn.querySelector('.eye-open');
      const eyeClosed = btn.querySelector('.eye-closed');

      if (input.type === 'password') {
        input.type = 'text';
        if (eyeOpen) eyeOpen.style.display = 'none';
        if (eyeClosed) eyeClosed.style.display = 'block';
      } else {
        input.type = 'password';
        if (eyeOpen) eyeOpen.style.display = 'block';
        if (eyeClosed) eyeClosed.style.display = 'none';
      }
    });
  });
}

/* --- Forgot Password Toast Alert --- */
function initForgotPassword() {
  const forgotLink = document.querySelector('.forgot-link');
  if (forgotLink) {
    forgotLink.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('To reset your credentials, please contact the RGM Transit Administration or your department coordinator.', 'info');
    });
  }
}

/* --- Role-Based Field Toggle (Signup) --- */
function initRoleToggle() {
  const roleSelect = document.getElementById('role');
  const driverFields = document.getElementById('driver-fields');
  const userBusFields = document.getElementById('user-bus-fields');
  const userStopFields = document.getElementById('user-stop-fields');

  if (!roleSelect) return;

  function toggleFields() {
    const role = roleSelect.value;

    if (driverFields) {
      driverFields.classList.toggle('visible', role === 'DRIVER');
      driverFields.querySelectorAll('input, select').forEach(el => {
        el.required = (role === 'DRIVER');
      });
    }
    if (userBusFields) {
      userBusFields.classList.toggle('visible', role === 'USER');
      userBusFields.querySelectorAll('select').forEach(el => {
        el.required = (role === 'USER');
      });
    }
    if (userStopFields) {
      userStopFields.classList.toggle('visible', role === 'USER');
      userStopFields.querySelectorAll('select').forEach(el => {
        el.required = (role === 'USER');
      });
    }
  }

  // Initial state
  toggleFields();
  roleSelect.addEventListener('change', toggleFields);
}

/* --- Bus → Stop Cascading Filter (Signup) --- */
function initBusStopFilter() {
  const busSelect = document.getElementById('busSelect');
  const stopSelect = document.getElementById('stopSelect');

  if (!busSelect || !stopSelect) return;

  // Store all options for filtering
  const allStops = Array.from(stopSelect.querySelectorAll('option[data-bus]'));

  busSelect.addEventListener('change', () => {
    const selectedBus = busSelect.value;

    allStops.forEach(opt => {
      if (opt.dataset.bus === selectedBus) {
        opt.style.display = '';
        opt.disabled = false;
      } else {
        opt.style.display = 'none';
        opt.disabled = true;
      }
    });

    // Reset stop selection
    stopSelect.value = '';
  });

  // Initial: hide all stops until bus is selected
  allStops.forEach(opt => {
    opt.style.display = 'none';
    opt.disabled = true;
  });
}

/* --- Client-Side Form Validation --- */
function initFormValidation() {
  const inputs = document.querySelectorAll('.form-input[required]');

  inputs.forEach(input => {
    input.addEventListener('blur', () => validateInput(input));
    input.addEventListener('input', () => {
      if (input.classList.contains('is-invalid')) {
        validateInput(input);
      }
    });
  });
}

function validateInput(input) {
  const value = input.value.trim();
  let isValid = true;

  // Required check
  if (!value) {
    isValid = false;
  }

  // Email check
  if (input.type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    isValid = emailRegex.test(value);
  }

  // Password minimum length
  if (input.type === 'password' && value) {
    isValid = value.length >= 6;
  }

  input.classList.toggle('is-valid', isValid && value !== '');
  input.classList.toggle('is-invalid', !isValid && (value !== '' || (input.hasAttribute('required') && input.dataset.touched)));

  // Mark as touched after first blur
  input.dataset.touched = 'true';

  return isValid;
}

/* --- Form Submit with Real Backend AJAX Calls --- */
function initFormSubmit() {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await handleAuthSubmit(loginForm, '/auth/login', 'Logging in...');
    });

    // 1-Click Demo Logins
    const demoStudentBtn = document.getElementById('demoStudentBtn');
    const demoDriverBtn = document.getElementById('demoDriverBtn');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (demoStudentBtn && emailInput && passwordInput) {
      demoStudentBtn.addEventListener('click', () => {
        emailInput.value = 'student@rgmcet.edu.in';
        passwordInput.value = 'Password123!';
        emailInput.classList.remove('is-invalid');
        emailInput.classList.add('is-valid');
        passwordInput.classList.remove('is-invalid');
        passwordInput.classList.add('is-valid');
        showToast('Demo Student credentials loaded! Logging in...', 'info');
        setTimeout(() => {
          loginForm.dispatchEvent(new Event('submit'));
        }, 400);
      });
    }

    if (demoDriverBtn && emailInput && passwordInput) {
      demoDriverBtn.addEventListener('click', () => {
        emailInput.value = 'driver@rgmcet.edu.in';
        passwordInput.value = 'Driver123!';
        emailInput.classList.remove('is-invalid');
        emailInput.classList.add('is-valid');
        passwordInput.classList.remove('is-invalid');
        passwordInput.classList.add('is-valid');
        showToast('Demo Captain/Driver credentials loaded! Logging in...', 'info');
        setTimeout(() => {
          loginForm.dispatchEvent(new Event('submit'));
        }, 400);
      });
    }
  }

  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await handleAuthSubmit(signupForm, '/auth/signup', 'Creating your account...');
    });
  }
}

async function handleAuthSubmit(form, endpoint, loadingMessage) {
  // Validate all required inputs
  const inputs = form.querySelectorAll('.form-input[required], .form-select[required]');
  let allValid = true;

  inputs.forEach(input => {
    input.dataset.touched = 'true';
    if (!validateInput(input)) {
      allValid = false;
    }
  });

  if (!allValid) {
    showToast('Please fill in all required fields correctly.', 'error');
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"], .btn--primary');
  const originalBtnContent = submitBtn ? submitBtn.innerHTML : '';
  
  if (submitBtn) {
    submitBtn.classList.add('btn--loading');
    submitBtn.disabled = true;
  }

  // Build JSON payload from form fields
  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    payload[key] = value;
  });

  try {
    const url = `${API_BASE}${endpoint}`;
    console.log(`[OmniTrack] Sending request to ${url}...`, payload);

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({ detail: 'Failed to parse response' }));

    if (!res.ok) {
      const errorMsg = data.detail || data.message || 'Operation failed. Please try again.';
      showToast(errorMsg, 'error');
      if (submitBtn) {
        submitBtn.classList.remove('btn--loading');
        submitBtn.disabled = false;
      }
      return;
    }

    // Success: store session
    if (data.token) {
      localStorage.setItem('omnitrack_token', data.token);
    }
    if (data.user) {
      localStorage.setItem('omnitrack_user', JSON.stringify(data.user));
    }

    showToast(data.message || 'Success!', 'success');

    // Smooth redirect to dashboard
    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 700);

  } catch (err) {
    console.error('[OmniTrack] Network error:', err);
    showToast(`Unable to connect to local server at ${API_BASE}. Make sure the server is running.`, 'error');
    if (submitBtn) {
      submitBtn.classList.remove('btn--loading');
      submitBtn.disabled = false;
    }
  }
}

/* --- Dashboard Real-Time State & Interaction --- */
function initDashboard() {
  const welcomeName = document.getElementById('welcomeName');
  if (!welcomeName) return; // Not on dashboard page

  // Check auth
  const userJson = localStorage.getItem('omnitrack_user');
  let user = null;

  if (userJson) {
    try {
      user = JSON.parse(userJson);
    } catch (e) {
      console.warn('Failed to parse user session');
    }
  }

  // Fallback to sample student if testing dashboard directly
  if (!user) {
    user = {
      name: "CHAKRIDHAR K",
      email: "student@rgmcet.edu.in",
      role: "USER",
      bus_name: "RGM-4thYear",
      stop_name: "KondaReddy Fort"
    };
  }

  // Populate UI
  welcomeName.textContent = `Welcome, ${user.name}!`;

  const userEmail = document.getElementById('userEmail');
  if (userEmail) userEmail.textContent = user.email;

  const roleBadge = document.getElementById('roleBadge');
  if (roleBadge) {
    if (user.role === 'DRIVER') {
      roleBadge.className = 'dash-badge dash-badge--driver';
      roleBadge.innerHTML = '<i class="fa-solid fa-id-badge"></i> Captain / Driver';
    } else {
      roleBadge.className = 'dash-badge';
      roleBadge.innerHTML = '<i class="fa-solid fa-graduation-cap"></i> Student';
    }
  }

  const cardBusName = document.getElementById('cardBusName');
  if (cardBusName) cardBusName.textContent = user.bus_name || 'RGM-4thYear';

  const liveRouteName = document.getElementById('liveRouteName');
  if (liveRouteName) liveRouteName.textContent = user.bus_name || 'RGM-4thYear';

  const cardStopName = document.getElementById('cardStopName');
  if (cardStopName) {
    cardStopName.textContent = user.stop_name || (user.role === 'DRIVER' ? (user.phone || 'Driver Active') : 'KondaReddy Fort');
  }

  // Logout handler
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      const token = localStorage.getItem('omnitrack_token');
      try {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
      } catch (e) {
        // Ignore network errors on logout
      }
      localStorage.removeItem('omnitrack_token');
      localStorage.removeItem('omnitrack_user');
      showToast('Logged out successfully.', 'info');
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 500);
    });
  }

  // Simulate Next Stop
  // Initialize Real-Time Leaflet GPS Map & Telemetry HUD
  initLiveGpsTracking(user);
}

/* --- Real-Time Leaflet GPS Tracking & Telemetry System --- */
function initLiveGpsTracking(user) {
  const mapElement = document.getElementById('liveGpsMap');
  const routeProgress = document.getElementById('routeProgress');
  const routeBusMarker = document.getElementById('routeBusMarker');
  const currentStopLabel = document.getElementById('currentStopLabel');

  const hudCoords = document.getElementById('hudCoords');
  const hudSpeed = document.getElementById('hudSpeed');
  const hudHeading = document.getElementById('hudHeading');
  const hudCountdown = document.getElementById('hudCountdown');
  const hudNextStop = document.getElementById('hudNextStop');
  const hudSatellites = document.getElementById('hudSatellites');

  const cardDriverSpeed = document.getElementById('cardDriverSpeed');
  const cardEta = document.getElementById('cardEta');

  // Fallback waypoints if route-data.js is not loaded
  const defaultWaypoints = [
    { name: "KondaReddy Fort (Kurnool)", lat: 15.82811, lng: 78.03729, time: "07:30 AM", etaSec: 360 },
    { name: "Control Room & Rajvihar", lat: 15.82308, lng: 78.04021, time: "07:38 AM", etaSec: 540 },
    { name: "Sv Complex & Station Road", lat: 15.81639, lng: 78.04084, time: "07:44 AM", etaSec: 720 },
    { name: "Medical College & C Camp", lat: 15.79945, lng: 78.05045, time: "07:52 AM", etaSec: 900 },
    { name: "Nandyal Checkpost", lat: 15.79107, lng: 78.05348, time: "08:00 AM", etaSec: 1100 },
    { name: "G. Pullareddy Engg College", lat: 15.77028, lng: 78.06138, time: "08:08 AM", etaSec: 1300 },
    { name: "B. Thandrapadu Junction", lat: 15.71166, lng: 78.11804, time: "08:15 AM", etaSec: 1500 },
    { name: "Raaga Mayuri Highway Resorts", lat: 15.70416, lng: 78.13277, time: "08:22 AM", etaSec: 1750 },
    { name: "NH 40 Orvakal Rock Garden", lat: 15.6834, lng: 78.17421, time: "08:32 AM", etaSec: 2100 },
    { name: "Nannur Bus Stop", lat: 15.68151, lng: 78.17471, time: "08:42 AM", etaSec: 2500 },
    { name: "Gutupalli Tollway (NH 40)", lat: 15.65347, lng: 78.1764, time: "08:50 AM", etaSec: 2900 },
    { name: "Hussainapuram Junction", lat: 15.54718, lng: 78.29996, time: "08:58 AM", etaSec: 3300 },
    { name: "Kalvabugga Milestone", lat: 15.54288, lng: 78.30915, time: "09:08 AM", etaSec: 3800 },
    { name: "Panyam Bypass (NH 40)", lat: 15.49439, lng: 78.41112, time: "09:22 AM", etaSec: 4400 },
    { name: "Santiram Hospital & Medical College", lat: 15.48775, lng: 78.47781, time: "09:32 AM", etaSec: 4900 },
    { name: "RGM College (RGMCET) Campus", lat: 15.48586, lng: 78.48392, time: "09:45 AM", etaSec: 0 }
  ];

  const WAYPOINTS = (typeof window !== 'undefined' && window.NH40_WAYPOINTS && window.NH40_WAYPOINTS.length > 0)
    ? window.NH40_WAYPOINTS
    : defaultWaypoints;

  const HIGHWAY_ROUTE = (typeof window !== 'undefined' && window.NH40_HIGHWAY_ROUTE && window.NH40_HIGHWAY_ROUTE.length > 0)
    ? window.NH40_HIGHWAY_ROUTE
    : WAYPOINTS.map(wp => [wp.lat, wp.lng]);

  // Build high-resolution tracking samples (~60 highway points for smooth continuous bus driving)
  const trackingSamples = [];
  const sampleStep = Math.max(1, Math.floor(HIGHWAY_ROUTE.length / 60));
  for (let i = 0; i < HIGHWAY_ROUTE.length; i += sampleStep) {
    trackingSamples.push(HIGHWAY_ROUTE[i]);
  }
  if (trackingSamples[trackingSamples.length - 1] !== HIGHWAY_ROUTE[HIGHWAY_ROUTE.length - 1]) {
    trackingSamples.push(HIGHWAY_ROUTE[HIGHWAY_ROUTE.length - 1]);
  }

  let sampleIdx = 0;
  let isAutoTracking = true;
  let remainingSeconds = 465;
  let map = null;
  let busMarker = null;
  let routePolyline = null;

  // Bearing calculation for realistic HUD heading
  function getBearing(lat1, lon1, lat2, lon2) {
    const toRad = Math.PI / 180;
    const toDeg = 180 / Math.PI;
    const dLon = (lon2 - lon1) * toRad;
    const y = Math.sin(dLon) * Math.cos(lat2 * toRad);
    const x = Math.cos(lat1 * toRad) * Math.sin(lat2 * toRad) -
              Math.sin(lat1 * toRad) * Math.cos(lat2 * toRad) * Math.cos(dLon);
    let brng = Math.atan2(y, x) * toDeg;
    return (brng + 360) % 360;
  }

  function getCompassDirection(deg) {
    const dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const idx = Math.round(deg / 22.5) % 16;
    return dirs[idx];
  }

  // Initialize Leaflet Map if container exists
  if (mapElement && typeof L !== 'undefined') {
    try {
      const initialPoint = trackingSamples[0] || [WAYPOINTS[0].lat, WAYPOINTS[0].lng];

      map = L.map('liveGpsMap', {
        zoomControl: true,
        scrollWheelZoom: true
      }).setView([15.65, 78.26], 11);

      // Layer 1: Google Satellite Hybrid (HD Imagery + Highways, Roads & Town Labels) - PRIMARY DEFAULT
      const googleHybrid = L.tileLayer('https://mt{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        subdomains: ['0', '1', '2', '3'],
        attribution: '&copy; Google Maps Satellite Hybrid',
        maxZoom: 20
      });

      // Layer 2: Esri Satellite Hybrid (Esri World Imagery + Overlaid Transportation Roads + Places Labels)
      const esriImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Earthstar Geographics',
        maxZoom: 19
      });
      const esriTransportation = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        opacity: 0.95
      });
      const esriLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        opacity: 0.95
      });
      const esriHybrid = L.layerGroup([esriImagery, esriTransportation, esriLabels]);

      // Layer 3: OpenStreetMap Daylight Road Map
      const streetLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      });

      // Layer 4: Pure Satellite (Esri Imagery without road or place labels)
      const pureSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri Earthstar Geographics',
        maxZoom: 19
      });

      // Activate Google Satellite Hybrid by default for crystal clear terrain + highway roads!
      googleHybrid.addTo(map);

      // Interactive Map Layer Switcher (Top-Right)
      L.control.layers({
        "🛰️ Google Satellite Hybrid (HD + Roads & Labels)": googleHybrid,
        "🌍 Esri Satellite Hybrid (Satellite + Roads & Places)": esriHybrid,
        "🗺️ Daylight Street Map (OpenStreetMap)": streetLayer,
        "🌑 Pure Satellite (Terrain Only)": pureSatellite
      }, null, { position: 'topright' }).addTo(map);

      // Exact NH 40 Road Highway Polyline (Outer glowing blue/cyan casing)
      routePolyline = L.polyline(HIGHWAY_ROUTE, {
        color: '#0284c7',
        weight: 6,
        opacity: 0.95,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(map);

      // Route dashed center line for sleek highway look
      L.polyline(HIGHWAY_ROUTE, {
        color: '#ffffff',
        weight: 2,
        opacity: 0.9,
        dashArray: '6, 10'
      }).addTo(map);

      // Automatically frame the complete Kurnool to Nandyal corridor perfectly
      map.fitBounds(routePolyline.getBounds(), { padding: [35, 35] });

      // Waypoint Markers along the exact highway path
      WAYPOINTS.forEach((wp, i) => {
        const isTerminal = (i === 0 || i === WAYPOINTS.length - 1);
        const radius = isTerminal ? 8 : 5;
        const color = isTerminal ? '#ef4444' : '#0284c7';

        L.circleMarker([wp.lat, wp.lng], {
          radius: radius,
          fillColor: isTerminal ? '#ef4444' : '#ffffff',
          color: color,
          weight: 2.5,
          opacity: 1,
          fillOpacity: 0.95
        }).addTo(map).bindPopup(
          `<div style="font-family:'Inter',sans-serif; padding:4px;">` +
          `<strong style="font-size:13px; color:#ffffff;">${wp.name}</strong><br>` +
          `<span style="color:#38bdf8; font-weight:600; font-size:12px;">🕒 Scheduled: ${wp.time}</span><br>` +
          `<small style="color:#94a3b8;">Transit Stop ${i + 1} of ${WAYPOINTS.length} (NH 40)</small>` +
          `</div>`
        );
      });

      // Animated Bus Marker
      const busDivIcon = L.divIcon({
        className: 'bus-map-beacon',
        html: '<i class="fa-solid fa-bus"></i>',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      busMarker = L.marker(initialPoint, { icon: busDivIcon }).addTo(map);
      busMarker.bindPopup(`<strong>${user.bus_name || 'RGM-4thYear'}</strong><br><span style="color:#10b981;">● GPS Live Tracking Active</span><br><small style="color:#94a3b8;">Highway: NH 40 Kurnool &mdash; Nandyal</small>`);

    } catch (err) {
      console.warn('[OmniTrack] Map tile initialization error:', err);
    }
  }

  // Update telemetry and UI state
  function updateTelemetry(sIdx) {
    const pt = trackingSamples[sIdx] || trackingSamples[0];
    const nextPt = trackingSamples[Math.min(sIdx + 1, trackingSamples.length - 1)];
    const progressPct = Math.round((sIdx / (trackingSamples.length - 1)) * 100);

    // Calculate heading angle & compass
    const bearing = Math.round(getBearing(pt[0], pt[1], nextPt[0], nextPt[1]));
    const compass = getCompassDirection(bearing);

    // Speed fluctuation (42 - 58 km/h on highway, 32 - 40 in town)
    const isHighway = (sIdx > 5 && sIdx < trackingSamples.length - 5);
    const baseSpeed = isHighway ? 52 : 36;
    const randomSpeed = Math.floor(baseSpeed + Math.sin(sIdx) * 6);

    // Find closest waypoint and next upcoming waypoint
    let closestWpIdx = 0;
    let closestDist = Infinity;
    WAYPOINTS.forEach((wp, i) => {
      const dLat = wp.lat - pt[0];
      const dLng = wp.lng - pt[1];
      const dist = (dLat * dLat) + (dLng * dLng);
      if (dist < closestDist) {
        closestDist = dist;
        closestWpIdx = i;
      }
    });

    const currWp = WAYPOINTS[closestWpIdx];
    const nextWp = WAYPOINTS[Math.min(closestWpIdx + 1, WAYPOINTS.length - 1)];

    if (hudCoords) hudCoords.textContent = `${pt[0].toFixed(4)}° N, ${pt[1].toFixed(4)}° E`;
    if (hudSpeed) hudSpeed.textContent = `${randomSpeed} km/h`;
    if (hudHeading) hudHeading.textContent = `${bearing}° ${compass}`;
    if (hudNextStop) hudNextStop.textContent = nextWp.name;
    if (hudSatellites) hudSatellites.textContent = `${10 + (sIdx % 3)} Locked`;

    if (cardDriverSpeed) cardDriverSpeed.textContent = `${randomSpeed} km/h`;
    if (cardEta) cardEta.textContent = `${Math.max(1, Math.round(remainingSeconds / 60))} mins`;
    if (currentStopLabel) currentStopLabel.textContent = currWp.name;

    // Timeline line progress
    if (routeProgress) routeProgress.style.width = `${progressPct}%`;
    if (routeBusMarker) routeBusMarker.style.left = `calc(3rem + ${progressPct}% - 20px)`;

    // Leaflet marker update
    if (busMarker && map) {
      busMarker.setLatLng([pt[0], pt[1]]);
      if (isAutoTracking) {
        map.panTo([pt[0], pt[1]], { animate: true, duration: 1 });
      }
    }
  }

  // Periodic GPS Tick (glides bus along highway every 3.5 seconds)
  const gpsInterval = setInterval(() => {
    if (!isAutoTracking) return;

    sampleIdx = (sampleIdx + 1) % trackingSamples.length;
    remainingSeconds = Math.max(30, remainingSeconds - 30);
    updateTelemetry(sampleIdx);
  }, 3200);

  // Second-by-second ETA countdown
  const timerInterval = setInterval(() => {
    if (remainingSeconds > 0) {
      remainingSeconds--;
    } else {
      remainingSeconds = 480;
    }
    const mins = Math.floor(remainingSeconds / 60).toString().padStart(2, '0');
    const secs = (remainingSeconds % 60).toString().padStart(2, '0');
    if (hudCountdown) {
      hudCountdown.textContent = `${mins}m ${secs}s`;
    }
  }, 1000);

  // Control: Auto-Track Toggle
  const toggleBtn = document.getElementById('toggleGpsTrackingBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      isAutoTracking = !isAutoTracking;
      toggleBtn.className = isAutoTracking ? 'btn btn--primary' : 'btn btn--outline';
      toggleBtn.innerHTML = isAutoTracking
        ? '<i class="fa-solid fa-circle-play"></i> <span>Auto-Track GPS (Live: ON)</span>'
        : '<i class="fa-solid fa-circle-pause"></i> <span>Auto-Track GPS (PAUSED)</span>';
      showToast(isAutoTracking ? 'Live GPS tracking auto-tracking resumed.' : 'Live GPS tracking paused.', 'info');
    });
  }

  // Control: Center on Bus
  const centerBtn = document.getElementById('centerMapBtn');
  if (centerBtn && map) {
    centerBtn.addEventListener('click', () => {
      const pt = trackingSamples[sampleIdx];
      map.setView([pt[0], pt[1]], 14, { animate: true });
      showToast(`Camera centered on ${user.bus_name || 'RGM-4thYear'}`, 'info');
    });
  }

  // Control: Full Route Fit
  const fitBtn = document.getElementById('fitRouteBtn');
  if (fitBtn && map && routePolyline) {
    fitBtn.addEventListener('click', () => {
      map.fitBounds(routePolyline.getBounds(), { padding: [35, 35] });
      showToast('Zoomed out to full transit route corridor (Kurnool to Nandyal).', 'info');
    });
  }

  // Control: Next Stop
  const simTripBtn = document.getElementById('simTripBtn');
  if (simTripBtn) {
    simTripBtn.addEventListener('click', () => {
      // Advance to next milestone waypoint
      sampleIdx = (sampleIdx + 5) % trackingSamples.length;
      updateTelemetry(sampleIdx);
      showToast(`Telemetry advanced along NH 40 route`, 'info');
    });
  }

  // Initial render
  updateTelemetry(0);
}

/* --- Toast Notification System --- */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: 'fa-circle-check',
    error: 'fa-circle-xmark',
    warning: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i> <span>${message}</span>`;

  container.appendChild(toast);

  // Auto-remove after 4.5 seconds
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(30px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}
