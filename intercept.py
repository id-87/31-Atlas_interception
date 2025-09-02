# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from models import *
from orbital import AtlasTracker
from mission import MissionPlanner
import math

app = FastAPI(
    title="31/ATLAS Mission Control",
    description="Intercept the mysterious interstellar visitor!",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])


atlas_tracker = AtlasTracker()
mission_planner = MissionPlanner()

@app.get("/")
async def root():
    return {"message": "🛸 31/ATLAS Mission Control Online", "status": "tracking"}

@app.get("/atlas/status", response_model=AtlasStatus)
async def get_atlas_status():
    """Get current ATLAS position and status"""
    pos = atlas_tracker.get_current_position()
    speed = atlas_tracker.calculate_speed(datetime.now())
    distance_earth = atlas_tracker.distance_from_earth(pos, datetime.now())
    distance_sun = math.sqrt(pos.x**2 + pos.y**2 + pos.z**2)
    
    return AtlasStatus(
        position=pos,
        velocity_kmh=speed * 3600,  
        distance_from_earth_au=distance_earth,
        distance_from_sun_au=distance_sun,
        last_updated=datetime.now()
    )

@app.post("/mission/plan", response_model=MissionResult)
async def plan_mission(request: MissionRequest):
    """Plan a mission to intercept ATLAS"""
    try:
        result = mission_planner.plan_mission(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mission/optimal-windows")
async def get_launch_windows():
    """Find the best launch windows in the next year"""
    windows = []
    base_date = datetime.now()
    
    for days in range(0, 365, 30):
        window_date = base_date + timedelta(days=days)
        atlas_pos = atlas_tracker.get_position_at_date(window_date)
        distance = atlas_tracker.distance_from_earth(atlas_pos, window_date)
        
        
        score = max(0, 10 - distance)
        
        windows.append({
            "date": window_date.strftime("%Y-%m-%d"),
            "score": round(score, 1),
            "atlas_distance_au": round(distance, 2),
            "description": f"Launch efficiency: {score:.1f}/10"
        })
    
    return sorted(windows, key=lambda x: x["score"], reverse=True)[:6]