from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import psutil

from database import SessionLocal, ThreatLog, engine
from security import security_engine

app = FastAPI(title="CyberFrame Core API")

# Setup CORS to allow the React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # Start the background security engine to generate threats
    security_engine.start()

@app.get("/api/health")
def get_system_health():
    # Use psutil to get real system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    return {
        "status": "Secure",
        "cpu_usage": cpu_percent,
        "memory_usage": memory.percent,
        "active_endpoints": 1402,
        "network_health": 99.98,
        "total_threats_blocked": security_engine.total_threats_blocked
    }

@app.get("/api/threats")
def get_recent_threats(db: Session = Depends(get_db), limit: int = 10):
    threats = db.query(ThreatLog).order_by(ThreatLog.timestamp.desc()).limit(limit).all()
    
    # Format for the frontend
    result = []
    for t in threats:
        result.append({
            "id": t.threat_id,
            "ip": t.ip_address,
            "type": t.detection_type,
            "severity": t.severity,
            "status": t.status,
            "time": t.timestamp.isoformat() + "Z"
        })
    return result

@app.post("/api/scan")
def run_manual_scan():
    return {"message": "Manual deep scan initiated across all endpoints."}
