import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from gpu_m import read_gpu
from agent import agent
from typing import Set
import json

latest_diagnosis: dict ={}
diagnose_every_n =3
poll_count=0
latest_metric: dict = {}
clients: Set[WebSocket]=set()

async def monitor_loop():
    global latest_metric
    while True:
        try:
            metrics = read_gpu()
            if metrics is None:
                await asyncio.sleep(3)
                continue
            latest_metric = metrics.to_dict()
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
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)

@app.post("/diagnose")
async def get_diagnose():
    metrics=read_gpu()
    if metrics is None:
        return JSONResponse({"error": "no GPU"}, status_code=503)
    diagnosis = agent.diagnosis(metrics)
    return JSONResponse({"metrics": metrics.to_dict(), "diagnosis": diagnosis})