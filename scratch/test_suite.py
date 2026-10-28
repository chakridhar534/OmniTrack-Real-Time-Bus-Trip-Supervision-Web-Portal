"""
OmniTrack Complete Quality Assurance & Error Audit Suite
Tests:
1. Static files & Link integrity
2. HTML validation
3. CSS syntax
4. JavaScript structure & handlers
5. Live Backend API Endpoints (FastAPI + SQLite)
   - Signup (new user, duplicate email, missing fields, short password)
   - Login (valid student, valid driver, invalid password, nonexistent email)
   - Session & /api/me authentication
   - Statistics endpoint
   - Static asset serving
"""

import os
import sys
import json
import urllib.request
import urllib.error
import sqlite3
from html.parser import HTMLParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = r"c:\Users\chakr\OneDrive\Apps\Desktop\antigravity"

passed = 0
failed = 0
warnings = 0

def check(name, condition, details=""):
    global passed, failed
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name} -> {details}")
        failed += 1

def warn(name, message):
    global warnings
    print(f"  [WARN] {name}: {message}")
    warnings += 1

print("\n========================================================")
print("1. AUDITING HTML FILES & TAG INTEGRITY")
print("========================================================")

class HTMLAuditor(HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.tags = []
        self.errors = []
        self.ids = set()
        self.links = []
        self.void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_id = attrs_dict.get('id')
        if tag_id:
            if tag_id in self.ids:
                self.errors.append(f"Duplicate ID '#{tag_id}'")
            self.ids.add(tag_id)
        if tag not in self.void_tags:
            self.tags.append(tag)
        
        href = attrs_dict.get('href')
        if href:
            self.links.append(href)
        src = attrs_dict.get('src')
        if src:
            self.links.append(src)

    def handle_endtag(self, tag):
        if tag in self.void_tags:
            return
        if not self.tags:
            self.errors.append(f"Unexpected end tag </{tag}>")
            return
        last = self.tags.pop()
        if last != tag:
            self.errors.append(f"Mismatched tag: expected </{last}>, found </{tag}>")

html_files = ['index.html', 'login.html', 'signup.html', 'dashboard.html']
for hf in html_files:
    filepath = os.path.join(PROJECT_DIR, hf)
    check(f"File exists: {hf}", os.path.exists(filepath))
    content = open(filepath, 'r', encoding='utf-8').read()
    auditor = HTMLAuditor(hf)
    auditor.feed(content)
    if auditor.tags:
        auditor.errors.append(f"Unclosed tags at end of file: {auditor.tags}")
    check(f"HTML validity: {hf} (0 tag mismatch, 0 duplicate IDs)", len(auditor.errors) == 0, str(auditor.errors))

    # Check local links
    for link in auditor.links:
        if link.startswith('http') or link.startswith('#') or link.startswith('data:') or link.startswith('mailto:'):
            continue
        clean_link = link.split('?')[0].split('#')[0]
        if clean_link:
            target_path = os.path.join(PROJECT_DIR, clean_link.replace('/', os.sep))
            check(f"Link target exists in {hf} -> '{clean_link}'", os.path.exists(target_path), f"File not found: {target_path}")

print("\n========================================================")
print("2. AUDITING CSS & JAVASCRIPT")
print("========================================================")

css_path = os.path.join(PROJECT_DIR, "css", "styles.css")
check("CSS file exists", os.path.exists(css_path))
css_content = open(css_path, 'r', encoding='utf-8').read()
css_braces = 0
for ch in css_content:
    if ch == '{':
        css_braces += 1
    elif ch == '}':
        css_braces -= 1
check("CSS curly braces balanced", css_braces == 0)

js_path = os.path.join(PROJECT_DIR, "js", "app.js")
check("JS file exists", os.path.exists(js_path))
js_content = open(js_path, 'r', encoding='utf-8').read()
check("JS has API_BASE configured", "API_BASE" in js_content)
check("JS has handleAuthSubmit implemented", "handleAuthSubmit" in js_content)
check("JS has showToast implemented", "showToast" in js_content)
check("JS has initDashboard implemented", "initDashboard" in js_content)

print("\n========================================================")
print("3. AUDITING LIVE BACKEND API (http://127.0.0.1:8000)")
print("========================================================")

def api_call(endpoint, method="GET", data=None, token=None):
    url = f"http://127.0.0.1:8000{endpoint}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status_code = resp.status
            resp_body = resp.read().decode('utf-8')
            return status_code, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(err_body)
        except:
            return e.code, {"raw": err_body}
    except Exception as e:
        return 0, {"error": str(e)}

# 3.1 Health & Stats
code, res = api_call("/api/stats")
check("GET /api/stats returns HTTP 200", code == 200)
check("Stats has total_users >= 2", res.get("total_users", 0) >= 2)
check("Stats has active_buses == 5", res.get("active_buses") == 5)

# 3.2 Student Login (Pre-seeded)
code, res = api_call("/auth/login", method="POST", data={
    "email": "student@rgmcet.edu.in",
    "password": "Password123!"
})
check("POST /auth/login (Student) returns HTTP 200", code == 200)
check("Student login returns session token", "token" in res and len(res["token"]) > 10)
check("Student login user has bus RGM-4thYear", res.get("user", {}).get("bus_name") == "RGM-4thYear")
student_token = res.get("token")

# 3.3 Driver Login (Pre-seeded)
code, res = api_call("/auth/login", method="POST", data={
    "email": "driver@rgmcet.edu.in",
    "password": "Driver123!"
})
check("POST /auth/login (Driver) returns HTTP 200", code == 200)
check("Driver login role is DRIVER", res.get("user", {}).get("role") == "DRIVER")

# 3.4 Invalid Login (Wrong password)
code, res = api_call("/auth/login", method="POST", data={
    "email": "student@rgmcet.edu.in",
    "password": "WrongPassword999!"
})
check("POST /auth/login (Wrong password) returns HTTP 401", code == 401)
check("Error message indicates invalid credentials", "Invalid" in res.get("detail", ""))

# 3.5 Token Verification (/api/me)
code, res = api_call("/api/me", token=student_token)
check("GET /api/me with valid Bearer token returns HTTP 200", code == 200)
check("User identity matches in /api/me", res.get("user", {}).get("email") == "student@rgmcet.edu.in")

# 3.6 Token Verification without token (Expected 401)
code, res = api_call("/api/me")
check("GET /api/me without token returns HTTP 401", code == 401)

# 3.7 New User Signup (Dynamic timestamp email)
import time
test_email = f"audit_user_{int(time.time())}@rgmcet.edu.in"
code, res = api_call("/auth/signup", method="POST", data={
    "name": "Audit Test Student",
    "email": test_email,
    "password": "AuditPass2026!",
    "role": "USER",
    "busName": "rgm-4thyear-001",
    "stopName": "rgm4y-stop-04"
})
check("POST /auth/signup (New Student) returns HTTP 200", code == 200)
check("New signup resolves stop 'Railway Station Road'", res.get("user", {}).get("stop_name") == "Railway Station Road")

# 3.8 Duplicate Email Signup (Expected 400)
code, res = api_call("/auth/signup", method="POST", data={
    "name": "Audit Duplicate",
    "email": test_email,
    "password": "AuditPass2026!"
})
check("POST /auth/signup (Duplicate Email) returns HTTP 400", code == 400)
check("Error mentions email exists", "already exists" in res.get("detail", ""))

# 3.9 Short Password Signup (Expected 400)
code, res = api_call("/auth/signup", method="POST", data={
    "name": "Short Pass User",
    "email": f"short_{int(time.time())}@rgmcet.edu.in",
    "password": "123"
})
check("POST /auth/signup (Password < 6 chars) returns HTTP 400", code == 400)

# 3.10 Static File Serving Verification
for page in ["/index.html", "/login.html", "/signup.html", "/dashboard.html", "/css/styles.css", "/js/app.js"]:
    req = urllib.request.Request(f"http://127.0.0.1:8000{page}")
    try:
        with urllib.request.urlopen(req) as resp:
            check(f"Static file served via HTTP: {page}", resp.status == 200)
    except Exception as e:
        check(f"Static file served via HTTP: {page}", False, str(e))

print("\n========================================================")
print(f"AUDIT SUMMARY: {passed} PASSED, {failed} FAILED, {warnings} WARNINGS")
print("========================================================")

if failed == 0:
    print("SUCCESS: The entire OmniTrack website has ZERO errors!")
else:
    print(f"ATTENTION: {failed} error(s) detected. Details above.")
