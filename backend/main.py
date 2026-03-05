import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from gpu_m import read_gpu
from agent import agent
from typing import Set
import json
import time
from collections import deque

latest_diagnosis: dict ={}
diagnose_every_n =3
poll_count=0
latest_metric: dict = {}
clients: Set[WebSocket]=set()
events: deque =deque(maxlen=200)

def make_event(metrics:dict, diagnosis:dict)-> dict | None:
    status= diagnosis.get("status", "healthy")
    bottleneck=diagnosis.get("status", "none")
    if status!= "healhty" or bottleneck not in ("none", "compute_bound"):
        return {
            "id":f"evt- {int(time.time()*1000)}",
            "time":time.strftime("%H:%M:%S"),
            "timestamp":time.time(),
            "status":status,
            "headline":diagnosis.get("headline", ""),
            "bottleneck":bottleneck
        }
    return None

async def monitor_loop():
    global latest_metric
    while True:
        try:
            metrics = read_gpu()
            if metrics is None:
                await asyncio.sleep(poll_count)
                continue

            latest_metric = metrics.to_dict()
            poll_count+=1

            if poll_count% diagnose_every_n==0:
                latest_diagnosis=agent.diagnosis(metrics)
                event=make_event(latest_metric, latest_diagnosis)
                if event:
                    events.appendleft(event)

            payload={
                "type":"update",
                "metrics":latest_metric,
                "diagnosis":latest_diagnosis,
                "events": list(events)[:20]
            }
            await broadcast(payload)
        except Exception as e:
            print(f"[monitor] error: {e}")
        await asyncio.sleep(3)

async def broadcast(payload:dict):
    dead=set()
    for s in clients:
        try:
            await s.send_text(json.dumps(payload))
        except Exception:
            dead.add(s)
        clients.difference_update(dead)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(monitor_loop())
    yield

app = FastAPI(title="watcher api", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])

@app.get("/health")
async def health():
    return {"ok":True}

@app.get("/metrics")
async def metrics():
    return JSONResponse({"metrics":latest_metric})

@app.websocket("/s")
async def ws_endppint(websocket:WebSocket):
    await websocket.accept()
    clients.add(WebSocket)
    if latest_metric:
        await websocket.send_text(json.dumps({
            "type":"update",
            "metrics":latest_metric,
            "diagnosis":latest_diagnosis,
            "events":list(events)[:20]
        }))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)

@app.get("/events")
async def get_events():
    return JSONResponse({"events": list(events)})

@app.post("/diagnose")
async def get_diagnose():
    metrics=read_gpu()
    if metrics is None:
        return JSONResponse({"error": "no GPU"}, status_code=503)
    diagnosis = agent.diagnosis(metrics)
    return JSONResponse({"metrics": metrics.to_dict(), "diagnosis": diagnosis})