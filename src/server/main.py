from fastapi import FastAPI, HTTPException
from typing import List
import redis
import uuid
import json
import os
import asyncio
from contextlib import asynccontextmanager

from src.server.models import Worker, InferenceRequest, InferenceResponse, InferenceResult

# --- Worker Cache ---
worker_cache: List[Worker] = []
cache_refresh_event = asyncio.Event()

# Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

async def refresh_worker_cache():
    """Periodically refreshes the worker cache from Redis."""
    while True:
        try:
            global worker_cache
            new_worker_list = []
            for key in redis_client.scan_iter("worker:*"):
                worker_data = redis_client.get(key)
                if worker_data:
                    new_worker_list.append(Worker.model_validate_json(worker_data))
            worker_cache = new_worker_list
            print(f"Worker cache refreshed. Found {len(worker_cache)} workers.")
        except Exception as e:
            print(f"Error refreshing worker cache: {e}")

        try:
            await asyncio.wait_for(cache_refresh_event.wait(), timeout=30)
            cache_refresh_event.clear()
        except asyncio.TimeoutError:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    asyncio.create_task(refresh_worker_cache())
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/register", status_code=201)
async def register_worker(worker: Worker):
    """Registers a new worker."""
    print(f"Registering worker: {worker.worker_id}")
    redis_client.set(f"worker:{worker.worker_id}", worker.model_dump_json(), ex=60) #expire after 60s
    cache_refresh_event.set()
    return {"message": "Worker registered successfully", "worker_id": worker.worker_id}

@app.get("/workers", response_model=List[Worker])
async def get_workers() -> List[Worker]:
    """Returns a list of all registered workers from the cache."""
    return worker_cache

@app.post("/inference", response_model=InferenceResponse)
async def create_inference_job(request: InferenceRequest):
    """Creates a new inference job and queues it for a worker."""
    compatible_workers = [
        worker
        for worker in worker_cache
        if request.model in worker.supported_models
    ]

    if not compatible_workers:
        raise HTTPException(status_code=400, detail="No available worker for the requested model")

    worker_index = redis_client.incr("worker_index") % len(compatible_workers)
    target_worker = compatible_workers[worker_index]

    request_id = str(uuid.uuid4())

    job = {
        "request_id": request_id,
        "model": request.model,
        "prompt": request.prompt,
        "params": request.params,
    }

    redis_client.lpush(f"queue:{target_worker.worker_id}", json.dumps(job))

    return InferenceResponse(
        request_id=request_id,
        message="Inference job queued successfully"
    )

@app.get("/result/{request_id}", response_model=InferenceResult)
async def get_result(request_id: str):
    """Retrieves the result of an inference job."""
    result = redis_client.get(f"result:{request_id}")
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    return InferenceResult.model_validate_json(result)
