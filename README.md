# OmniTrack: Real-Time Bus & Trip Supervision Web Portal

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![Leaflet](https://img.shields.io/badge/Leaflet.js-Interactive%20Maps-199900?logo=leaflet)
![License](https://img.shields.io/badge/License-MIT-green)

**OmniTrack** is a full-stack, real-time college bus tracking and trip supervision web platform tailored for institutional transit operations (specifically designed around the **Kurnool to RGM College, Nandyal route along NH 40**).

It enables students to view live bus locations, estimated arrival times (ETA), and route progress, while empowering transport supervisors and drivers with real-time fleet telemetry, trip monitoring, and account management.

---

## 🌟 Key Features

### 📍 1. Live GPS Telemetry & Interactive Map
- **High-Precision Mapping:** Powered by [Leaflet.js](https://leafletjs.com/), rendering snapped highway waypoints and official transit corridors along NH 40.
- **Real-Time Bus Metrics:** Displays live vehicle coordinates (`lat`, `lng`), speed (km/h), heading angle, route progress percentage, battery percentage, and active satellite count.
- **Stop-by-Stop Progress:** Tracks 19 major boarding and drop-off points (from *KondaReddy Fort* and *Control Room* through *C Camp*, *Nandyal Checkpost*, to *RGM College*).

### 👥 2. Role-Based Access Control
- **Students (`USER`):** Access customized bus schedules, view assigned buses and boarding stops, track current bus position, and calculate dynamic ETAs.
- **Drivers / Fleet Captains (`DRIVER`):** View fleet assignments, passenger manifests, route waypoints, and broadcast live location updates.
- **Secure Authentication:** Built-in password hashing using salted **SHA-256**, token-based session management, and role-protected API endpoints.

### 📊 3. Supervisory Dashboard
- High-level overview of active buses, total registered students, on-duty drivers, and monitored transit stops.
- Live vehicle status indicators (`LIVE_TRANSIT`, speed warnings, vehicle registration numbers, driver direct dial links).

---

## 🏗️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), Pydantic, SQLite3 |
| **Frontend** | HTML5, CSS3 (Modern Glassmorphic UI), Vanilla JavaScript (ES6+ Modules) |
| **Mapping & Geospatial** | Leaflet.js, OpenStreetMap Tiles, Custom Snapped GeoJSON / Coordinates |
| **Icons & Typography** | FontAwesome 6.5, Google Fonts (*Outfit* & *Inter*) |

---

## 📁 Repository Structure

```text
├── css/
│   └── styles.css          # Glassmorphic UI design, responsive layout, animations
├── js/
│   ├── app.js              # Frontend client application logic, map engine & polling
│   └── route-data.js       # Pre-computed route paths, stop definitions & waypoints
├── scratch/                # Geolocation processing, snapping & audit scripts
│   ├── build_route_data.ps1
│   ├── convert_coords.ps1
│   ├── deep_audit.py
│   ├── generate_stops.py
│   └── snap_waypoints.ps1
├── dashboard.html          # Real-time supervision dashboard
├── index.html              # Landing page and features showcase
├── login.html              # Authentication portal (Students & Drivers)
├── signup.html             # User registration with bus & stop assignment
├── omnitrack.db            # SQLite database for accounts and sessions
├── server.py               # FastAPI backend with REST endpoints & static file hosting
├── start_server.bat        # Windows one-click start script
└── .gitignore              # Git ignore rules for Python bytecode and caches
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** installed on your system.
- Standard web browser (Chrome, Edge, Firefox, Safari).

### 1. Clone the Repository
```bash
git clone https://github.com/chakridhar534/OmniTrack-Real-Time-Bus-Trip-Supervision-Web-Portal.git
cd OmniTrack-Real-Time-Bus-Trip-Supervision-Web-Portal
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install fastapi uvicorn pydantic python-multipart
```

### 3. Launch the Application

#### On Windows:
Double-click `start_server.bat` or run:
```cmd
start_server.bat
```

#### On Linux / macOS / Terminal:
```bash
python server.py
```

The server will automatically initialize `omnitrack.db` with sample seed accounts and bind to `http://localhost:8000`.

---

## 🌐 Application URLs

Once the server is running, open your browser:

- **Homepage:** [http://localhost:8000/index.html](http://localhost:8000/index.html)
- **Live Dashboard:** [http://localhost:8000/dashboard.html](http://localhost:8000/dashboard.html)
- **Sign In:** [http://localhost:8000/login.html](http://localhost:8000/login.html)
- **Registration:** [http://localhost:8000/signup.html](http://localhost:8000/signup.html)
- **Interactive API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔑 Demo Credentials

The backend seeds demo accounts upon the first run for testing:

| Role | Email | Password | Assigned Route |
| :--- | :--- | :--- | :--- |
| **Student** | `student@rgmcet.edu.in` | `Password123!` | RGM-4thYear (KondaReddy Fort) |
| **Driver** | `driver@rgmcet.edu.in` | `Driver123!` | RGM-4thYear (Captain Ramesh Kumar) |

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/signup` | Register a student or driver account with route & stop preferences |
| `POST` | `/auth/login` | Authenticate credentials and receive a session token |
| `GET` | `/api/me` | Fetch profile and route details for current session |
| `POST` | `/auth/logout` | Terminate session and invalidate auth token |
| `GET` | `/api/stats` | Retrieve platform statistics (users, buses, stops) |
| `GET` | `/api/buses/{bus_id}/gps` | Get real-time GPS telemetry for a specified bus |
| `POST` | `/api/buses/{bus_id}/gps` | Update telemetry data for a bus |
| `GET` | `/api/gps/all` | Fetch telemetry data for all active fleet vehicles |

---

## 👤 Author

- **CHAKRIDHAR K** - [chakridhar534](https://github.com/chakridhar534)

