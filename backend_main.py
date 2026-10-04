from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import random, math, time, hashlib, secrets
from typing import Optional

app = FastAPI(title='AXORA Intelligence API', version='0.1.0')
BASE_DIR = Path(__file__).resolve().parent
app.mount('/assets', StaticFiles(directory=str(BASE_DIR / 'assets')), name='assets')

@app.get('/', include_in_schema=False)
def serve_app():
    return FileResponse(str(BASE_DIR / 'app.html'))
USERS = {}
TOKENS = {}

def hash_password(password: str, salt: Optional[str] = None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120_000).hex()
    return f'{salt}${digest}'

def verify_password(password: str, stored: str):
    try:
        salt, digest = stored.split('$', 1)
        check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120_000).hex()
        return secrets.compare_digest(check, digest)
    except Exception:
        return False

def seed_user(email, name, password):
    USERS[email.lower()] = {'name': name, 'email': email.lower(), 'password_hash': hash_password(password)}

seed_user('operator@factory.com', 'Factory Operator', 'AXORA@1234')

class AuthRequest(BaseModel):
    identifier: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None

class GoogleDemoRequest(BaseModel):
    email: str
    name: str

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


DEMO_DURATION_SEC = 75
_demo_started_at = None

PHASES = [
    (0, 15, 'NORMAL', 'Stable production window', 'No intervention required'),
    (15, 30, 'ENERGY DRIFT', 'Energy consumption is rising above baseline', 'Watch energy/unit'),
    (30, 45, 'PROCESS DEVIATION', 'Thermal and vibration signals are drifting', 'Inspect operating window'),
    (45, 60, 'QUALITY RISK', 'AXORA predicts an elevated quality-deviation risk', 'Intervention recommended'),
    (60, 75, 'RECOVERY', 'Operator action is reducing process risk', 'Verify stabilization'),
]


def start_demo():
    global _demo_started_at
    _demo_started_at = time.time()
    return demo_status()


def demo_status():
    global _demo_started_at
    if _demo_started_at is None:
        return {'running': False, 'elapsed_sec': 0, 'phase': 'READY', 'label': 'Ready to start live scenario', 'action': 'Start demo'}
    elapsed = time.time() - _demo_started_at
    if elapsed >= DEMO_DURATION_SEC:
        return {'running': False, 'elapsed_sec': DEMO_DURATION_SEC, 'phase': 'COMPLETE', 'label': 'Scenario complete — process stabilized', 'action': 'Replay demo'}
    for start, end, phase, label, action in PHASES:
        if start <= elapsed < end:
            return {'running': True, 'elapsed_sec': round(elapsed, 1), 'phase': phase, 'label': label, 'action': action, 'remaining_sec': round(end-elapsed, 1)}
    return {'running': False, 'elapsed_sec': 0, 'phase': 'READY', 'label': 'Ready to start live scenario', 'action': 'Start demo'}


def scenario_telemetry():
    status = demo_status()
    if not status['running']:
        # Keep the final state after completion; otherwise use baseline.
        if status['phase'] == 'COMPLETE':
            progress = 1.0
        else:
            progress = 0.0
    else:
        progress = min(1.0, status['elapsed_sec'] / DEMO_DURATION_SEC)
    # Smooth rise through risk, then recovery.
    if progress < 0.20:
        x = progress / 0.20
        temp = 78.0 + 0.5*x; vib = 2.8 + 0.15*x; power = 42 + 0.8*x; epu = 3.25 + 0.05*x; prod = 130
    elif progress < 0.40:
        x = (progress-0.20)/0.20
        temp = 78.5 + 4.0*x; vib = 2.95 + 0.55*x; power = 42.8 + 4.0*x; epu = 3.30 + 0.32*x; prod = 130 - 2*x
    elif progress < 0.60:
        x = (progress-0.40)/0.20
        temp = 82.5 + 4.8*x; vib = 3.5 + 1.2*x; power = 46.8 + 5.5*x; epu = 3.62 + 0.42*x; prod = 128 - 6*x
    elif progress < 0.80:
        x = (progress-0.60)/0.20
        temp = 87.3 + 0.8*x; vib = 4.7 + 0.2*x; power = 52.3 + 0.8*x; epu = 4.04 + 0.05*x; prod = 122 - 2*x
    else:
        x = (progress-0.80)/0.20
        temp = 88.1 - 7.0*x; vib = 4.9 - 1.8*x; power = 53.1 - 7.0*x; epu = 4.09 - 0.62*x; prod = 120 + 9*x
    return Telemetry(temperature=temp, pressure=6.4, vibration=vib, power_kw=power, production_rate=prod, energy_per_unit=epu)

BASELINE = {
    'temperature': 78.0,
    'pressure': 6.4,
    'vibration': 2.8,
    'power_kw': 42.0,
    'production_rate': 130.0,
    'energy_per_unit': 3.25,
}

class Telemetry(BaseModel):
    temperature: float = Field(..., ge=0)
    pressure: float = Field(..., ge=0)
    vibration: float = Field(..., ge=0)
    power_kw: float = Field(..., ge=0)
    production_rate: float = Field(..., ge=0)
    energy_per_unit: float = Field(..., ge=0)


def pct_dev(x, b):
    return (x - b) / b * 100.0


def infer(t: Telemetry):
    # Transparent baseline-deviation model for the prototype.
    d = {
        'temperature': pct_dev(t.temperature, BASELINE['temperature']),
        'pressure': pct_dev(t.pressure, BASELINE['pressure']),
        'vibration': pct_dev(t.vibration, BASELINE['vibration']),
        'power_kw': pct_dev(t.power_kw, BASELINE['power_kw']),
        'production_rate': pct_dev(t.production_rate, BASELINE['production_rate']),
        'energy_per_unit': pct_dev(t.energy_per_unit, BASELINE['energy_per_unit']),
    }
    risk = 38 + 0.45 * max(d['energy_per_unit'], 0) + 0.28 * max(d['temperature'], 0) + 0.18 * max(d['vibration'], 0) + 0.12 * abs(d['production_rate'])
    risk = max(0, min(99, risk))
    confidence = max(72, min(98, 86 + 0.35 * abs(d['energy_per_unit']) + 0.15 * abs(d['temperature'])))
    severity = 'critical' if risk >= 75 else 'warning' if risk >= 55 else 'normal'
    contributors = sorted([
        ('Energy deviation', d['energy_per_unit']),
        ('Thermal drift', d['temperature']),
        ('Vibration', d['vibration']),
        ('Power draw', d['power_kw']),
    ], key=lambda x: abs(x[1]), reverse=True)[:3]
    recommendations = []
    if d['energy_per_unit'] > 8: recommendations.append('Reduce operating load by 5–8% and compare energy/unit against baseline.')
    if d['temperature'] > 5: recommendations.append('Inspect heating-cycle control and temperature sensor calibration.')
    if d['vibration'] > 15: recommendations.append('Inspect mechanical alignment and rotating components.')
    if not recommendations: recommendations.append('Maintain current operating window and continue monitoring.')
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'risk': round(risk, 1), 'confidence': round(confidence, 1), 'severity': severity,
        'deviations': {k: round(v, 2) for k, v in d.items()},
        'contributors': [{'name': n, 'deviation_pct': round(v, 2)} for n, v in contributors],
        'prediction_horizon_min': 18 if risk >= 65 else 30,
        'defect_probability': round(risk, 1),
        'recommendations': recommendations,
    }


def demo_telemetry():
    # A controllable scenario that makes the hackathon demo visually meaningful.
    drift = random.uniform(0, 1)
    return Telemetry(
        temperature=78 + 5.7 * drift,
        pressure=6.4 + random.uniform(-0.15, 0.25),
        vibration=2.8 + 1.4 * drift,
        power_kw=42 + 6.7 * drift,
        production_rate=130 - 5 * drift,
        energy_per_unit=3.25 + 0.59 * drift,
    )


@app.post('/api/auth/signup')
def auth_signup(req: AuthRequest):
    email = (req.email or '').strip().lower()
    name = (req.name or '').strip()
    password = req.password or ''
    if not email or '@' not in email or not name:
        raise HTTPException(status_code=400, detail='Enter a valid name and email.')
    if len(password) < 8:
        raise HTTPException(status_code=400, detail='Password must be at least 8 characters.')
    if email in USERS:
        raise HTTPException(status_code=409, detail='An account with this email already exists.')
    seed_user(email, name, password)
    token = secrets.token_urlsafe(32)
    TOKENS[token] = email
    return {'token': token, 'user': {'name': name, 'email': email}}

@app.post('/api/auth/login')
def auth_login(req: AuthRequest):
    identifier = (req.identifier or '').strip().lower()
    password = req.password or ''
    user = USERS.get(identifier)
    if not user:
        user = next((u for u in USERS.values() if u['email'] == identifier), None)
    if not user or not verify_password(password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid username/email or password.')
    token = secrets.token_urlsafe(32)
    TOKENS[token] = user['email']
    return {'token': token, 'user': {'name': user['name'], 'email': user['email']}}

@app.post('/api/auth/google-demo')
def auth_google_demo(req: GoogleDemoRequest):
    email = req.email.strip().lower()
    name = req.name.strip() or 'Google User'
    if email not in USERS:
        seed_user(email, name, secrets.token_urlsafe(18))
    token = secrets.token_urlsafe(32)
    TOKENS[token] = email
    return {'token': token, 'user': {'name': USERS[email]['name'], 'email': email, 'provider': 'google-demo'}}

@app.post('/api/auth/forgot')
def auth_forgot(req: AuthRequest):
    email = (req.email or '').strip().lower()
    return {'status': 'ok', 'message': f'Demo reset flow created for {email}'}

@app.get('/api/health')
def health():
    return {'status': 'ok', 'service': 'AXORA Intelligence API'}

@app.get('/api/telemetry')
def telemetry():
    t = scenario_telemetry() if _demo_started_at is not None else demo_telemetry()
    return {'telemetry': t.model_dump(), 'analysis': infer(t), 'scenario': demo_status()}

@app.post('/api/analyze')
def analyze(t: Telemetry):
    return {'telemetry': t.model_dump(), 'analysis': infer(t)}

@app.get('/api/dashboard')
def dashboard():
    t = scenario_telemetry() if _demo_started_at is not None else demo_telemetry()
    a = infer(t)
    return {
        'facility': 'Plant Alpha · Line 04',
        'mode': 'DEMO',
        'telemetry': t.model_dump(),
        'analysis': a,
        'scenario': demo_status(),
        'energy_efficiency': round(max(0, 100 - max(a['deviations']['energy_per_unit'], 0) * 0.55), 1),
        'process_health': round(max(0, 100 - a['risk'] * 0.11), 1),
    }


@app.post('/api/demo/start')
def demo_start():
    return start_demo()

@app.post('/api/demo/reset')
def demo_reset():
    global _demo_started_at
    _demo_started_at = None
    return demo_status()

@app.get('/api/demo/status')
def demo_state():
    return demo_status()
