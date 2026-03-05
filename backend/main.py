import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from gpu_m import read_gpu

latest_metric: dict = {}

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




