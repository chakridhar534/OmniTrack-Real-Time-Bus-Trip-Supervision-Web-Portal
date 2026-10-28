"""
OmniTrack Local Backend Server
Built with FastAPI and SQLite for local testing of real signups, logins, and live bus tracking.
"""

import os
import sqlite3
import hashlib
import secrets
from typing import Optional
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import re
from pydantic import BaseModel

# Base directory
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "omnitrack.db"

# Bus and Stop Reference Data
BUS_NAMES = {
    "rgm-1styear-001": "RGM-1stYear",
    "rgm-2ndyear-001": "RGM-2ndYear",
    "rgm-3rdyear-001": "RGM-3rdYear",
    "rgm-4thyear-001": "RGM-4thYear",
    "69120a57d863945152d75cdc": "RGM-3rdYear",
    "69134ab02313225bf5905fdc": "Shantiram-45"
}

STANDARD_STOPS = [
    "KondaReddy Fort",
    "Control Room",
    "Sv Complex",
    "Railway Station Road",
    "Rajhvihar",
    "Kurnool Medical College",
    "Collector Office",
    "Gayathri Estates",
    "Maddur Nagar",
    "C Camp",
    "Amma Hospital",
    "Nandyal Checkpost",
    "Maruthi Mega City",
    "G. Pullareddy Engineering College",
    "B. Thandrapadu",
    "B. Thandrapadu Lake View",
    "Raaga Mayuri Resorts",
    "Nannur",
    "RGM College"
]

STOP_NAMES = {}

# Map 1st, 2nd, 3rd, and 4th Year stops
for idx, stop in enumerate(STANDARD_STOPS, start=1):
    num_str = f"{idx:02d}"
    STOP_NAMES[f"rgm1y-stop-{num_str}"] = stop
    STOP_NAMES[f"rgm2y-stop-{num_str}"] = stop
    STOP_NAMES[f"rgm3y-stop-{num_str}"] = stop
    STOP_NAMES[f"rgm4y-stop-{num_str}"] = stop

# Legacy Hex IDs
LEGACY_HEX_STOPS = {
    "6912116b367dc1371e388855": "KondaReddy Fort",
    "691211d1367dc1371e388861": "Control Room",
    "69121205367dc1371e38886d": "Sv Complex",
    "69121240367dc1371e388879": "Railway Station Road",
    "6912125a367dc1371e388885": "Rajhvihar",
    "69121275367dc1371e388891": "Kurnool Medical College",
    "69121291367dc1371e38889d": "Collector Office",
    "691212ad367dc1371e3888a9": "Gayathri Estates",
    "691212c9367dc1371e3888b5": "Maddur Nagar",
    "691212fb367dc1371e3888c1": "C Camp",
    "69121314367dc1371e3888cd": "Amma Hospital",
    "6912132d367dc1371e3888d9": "Nandyal Checkpost",
    "69121348367dc1371e3888e5": "Maruthi Mega City",
    "69121365367dc1371e3888f1": "G. Pullareddy Engineering College",
    "69121380367dc1371e3888fd": "B. Thandrapadu",
    "69147880487fc475a4c3913d": "B. Thandrapadu Lake View",
    "691478bc487fc475a4c39149": "Raaga Mayuri Resorts",
    "6914791f487fc475a4c39155": "Nannur",
    "69147942487fc475a4c39161": "RGM College",
}
STOP_NAMES.update(LEGACY_HEX_STOPS)

def get_db():
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    check_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return secrets.compare_digest(check_hash, hashed)

def init_db():
    conn = get_db()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'USER',
                phone TEXT,
                bus_id TEXT,
                bus_name TEXT,
                stop_id TEXT,
                stop_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Seed pre-configured student and driver accounts if empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Sample Student
            s_hash, s_salt = hash_password("Password123!")
            conn.execute("""
                INSERT INTO users (name, email, password_hash, salt, role, phone, bus_id, bus_name, stop_id, stop_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "CHAKRIDHAR K",
                "student@rgmcet.edu.in",
                s_hash,
                s_salt,
                "USER",
                "9876543210",
                "rgm-4thyear-001",
                "RGM-4thYear",
                "rgm4y-stop-01",
                "KondaReddy Fort"
            ))

            # Sample Driver
            d_hash, d_salt = hash_password("Driver123!")
            conn.execute("""
                INSERT INTO users (name, email, password_hash, salt, role, phone, bus_id, bus_name, stop_id, stop_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Ramesh Kumar (Captain)",
                "driver@rgmcet.edu.in",
                d_hash,
                d_salt,
                "DRIVER",
                "9848022338",
                "rgm-4thyear-001",
                "RGM-4thYear",
                None,
                None
            ))
            print("[OMNITRACK] Seeded sample student (student@rgmcet.edu.in) and driver (driver@rgmcet.edu.in)")
        
        # Migrate any legacy route names
        conn.execute("UPDATE users SET bus_name = 'RGM-3rdYear' WHERE bus_name = 'RGM-NEW-3rdYear'")
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("[OMNITRACK] Database & Backend initialized")
    yield

app = FastAPI(title="OmniTrack Backend API", lifespan=lifespan)

# Allow CORS for file:// and localhost origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "USER"
    phone: Optional[str] = None
    assignedBus: Optional[str] = None
    busName: Optional[str] = None
    stopName: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/signup")
async def signup(req: Request):
    # Support both JSON and Form Data
    content_type = req.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await req.json()
    else:
        form = await req.form()
        data = dict(form)

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "USER").strip().upper()
    phone = data.get("phone", "").strip()
    assigned_bus = data.get("assignedBus", "").strip()
    bus_name_id = data.get("busName", "").strip()
    stop_name_id = data.get("stopName", "").strip()

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="Name, email, and password are required.")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    # Determine bus and stop
    bus_id = assigned_bus if role == "DRIVER" else bus_name_id
    bus_display = BUS_NAMES.get(bus_id, bus_id)
    stop_display = STOP_NAMES.get(stop_name_id, stop_name_id) if role == "USER" else None

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        pwd_hash, salt = hash_password(password)
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, salt, role, phone, bus_id, bus_name, stop_id, stop_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, pwd_hash, salt, role, phone, bus_id, bus_display, stop_name_id, stop_display))
        user_id = cursor.lastrowid

        # Create session
        token = secrets.token_hex(24)
        cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        conn.commit()

        user_info = {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "phone": phone,
            "bus_id": bus_id,
            "bus_name": bus_display,
            "stop_id": stop_name_id,
            "stop_name": stop_display
        }

        return {
            "success": True,
            "message": "Account created successfully!",
            "token": token,
            "user": user_info,
            "redirect": "/dashboard.html"
        }
    finally:
        conn.close()

@app.post("/auth/login")
async def login(req: Request):
    content_type = req.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await req.json()
    else:
        form = await req.form()
        data = dict(form)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please enter both email and password.")

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, password_hash, salt, role, phone, bus_id, bus_name, stop_id, stop_name
            FROM users WHERE email = ?
        """, (email,))
        row = cursor.fetchone()

        if not row or not verify_password(password, row["password_hash"], row["salt"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        # Create session token
        token = secrets.token_hex(24)
        cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, row["id"]))
        conn.commit()

        user_info = {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
            "phone": row["phone"],
            "bus_id": row["bus_id"],
            "bus_name": row["bus_name"],
            "stop_id": row["stop_id"],
            "stop_name": row["stop_name"]
        }

        return {
            "success": True,
            "message": "Login successful! Welcome back.",
            "token": token,
            "user": user_info,
            "redirect": "/dashboard.html"
        }
    finally:
        conn.close()

@app.get("/api/me")
async def get_current_user(token: Optional[str] = None, req: Request = None):
    # Check Authorization header first
    auth_header = req.headers.get("authorization", "") if req else ""
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="Authentication token required.")

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.role, u.phone, u.bus_id, u.bus_name, u.stop_id, u.stop_name, u.created_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        """, (token,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid or expired session token.")

        return {
            "success": True,
            "user": dict(row)
        }
    finally:
        conn.close()

@app.post("/auth/logout")
async def logout(req: Request):
    auth_header = req.headers.get("authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if token:
        conn = get_db()
        with conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.close()

    return {"success": True, "message": "Logged out successfully."}

@app.get("/api/stats")
async def get_stats():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'USER'")
        students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'DRIVER'")
        drivers = cursor.fetchone()[0]
        return {
            "total_users": total_users,
            "students": students,
            "drivers": drivers,
            "active_buses": 5,
            "active_stops": len(STOP_NAMES)
        }
    finally:
        conn.close()

# Real-Time GPS Telemetry Data for Buses (Kurnool -> NH 40 -> RGM College Nandyal)
LIVE_GPS_DATA = {
    "rgm-4thyear-001": {
        "bus_id": "rgm-4thyear-001",
        "bus_name": "RGM-4thYear",
        "driver_name": "Ramesh Kumar (Captain)",
        "driver_phone": "9848022338",
        "reg_no": "AP 21 TZ 4509",
        "lat": 15.8281,
        "lng": 78.0373,
        "speed": 42,
        "heading": 118,
        "current_stop": "KondaReddy Fort",
        "next_stop": "Nandyal Checkpost",
        "eta_minutes": 8,
        "status": "LIVE_TRANSIT",
        "battery_pct": 98,
        "satellites": 9,
        "route_progress_pct": 45
    },
    "rgm-3rdyear-001": {
        "bus_id": "rgm-3rdyear-001",
        "bus_name": "RGM-3rdYear",
        "driver_name": "Suresh Babu",
        "driver_phone": "9848011223",
        "reg_no": "AP 21 TZ 4210",
        "lat": 15.8150,
        "lng": 78.0550,
        "speed": 38,
        "heading": 115,
        "current_stop": "Control Room",
        "next_stop": "Amma Hospital",
        "eta_minutes": 12,
        "status": "LIVE_TRANSIT",
        "battery_pct": 94,
        "satellites": 8,
        "route_progress_pct": 38
    },
    "rgm-2ndyear-001": {
        "bus_id": "rgm-2ndyear-001",
        "bus_name": "RGM-2ndYear",
        "driver_name": "Venkatesh K",
        "driver_phone": "9848033445",
        "reg_no": "AP 21 TZ 3890",
        "lat": 15.8000,
        "lng": 78.0800,
        "speed": 46,
        "heading": 120,
        "current_stop": "Nandyal Checkpost",
        "next_stop": "B. Thandrapadu",
        "eta_minutes": 6,
        "status": "LIVE_TRANSIT",
        "battery_pct": 96,
        "satellites": 10,
        "route_progress_pct": 55
    },
    "rgm-1styear-001": {
        "bus_id": "rgm-1styear-001",
        "bus_name": "RGM-1stYear",
        "driver_name": "Anil Kumar",
        "driver_phone": "9848055667",
        "reg_no": "AP 21 TZ 2701",
        "lat": 15.7500,
        "lng": 78.1400,
        "speed": 40,
        "heading": 122,
        "current_stop": "B. Thandrapadu",
        "next_stop": "Raaga Mayuri Resorts",
        "eta_minutes": 10,
        "status": "LIVE_TRANSIT",
        "battery_pct": 92,
        "satellites": 9,
        "route_progress_pct": 68
    }
}

@app.get("/api/buses/{bus_id}/gps")
async def get_bus_gps(bus_id: str):
    # Lookup by bus_id or name
    gps = LIVE_GPS_DATA.get(bus_id)
    if not gps:
        for b_id, data in LIVE_GPS_DATA.items():
            if bus_id.lower() in b_id.lower() or bus_id.lower() in data["bus_name"].lower():
                return {"success": True, "gps": data}
        gps = LIVE_GPS_DATA["rgm-4thyear-001"]
    return {"success": True, "gps": gps}

@app.post("/api/buses/{bus_id}/gps")
async def update_bus_gps(bus_id: str, req: Request):
    data = await req.json()
    if bus_id in LIVE_GPS_DATA:
        LIVE_GPS_DATA[bus_id].update(data)
    return {"success": True, "gps": LIVE_GPS_DATA.get(bus_id, data)}

@app.get("/api/gps/all")
async def get_all_buses_gps():
    return {"success": True, "buses": list(LIVE_GPS_DATA.values())}

# Mount frontend static directory so http://localhost:8000/ serves the entire site
app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 62)
    print("  OMNITRACK LOCAL SERVER IS RUNNING!")
    print("  IMPORTANT: Keep this terminal window OPEN while browsing!")
    print("  -> Website URL:  http://localhost:8000/index.html")
    print("  -> Dashboard:    http://localhost:8000/dashboard.html")
    print("  -> API Docs:     http://localhost:8000/docs")
    print("  (Do NOT press Ctrl+C until you want to stop the server)")
    print("=" * 62 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

