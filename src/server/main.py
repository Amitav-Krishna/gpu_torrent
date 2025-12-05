from fastapi import FastAPI, HTTPException
from typing import List
import redis
import uuid
import json
import os

from src.server.models import Worker, InferenceRequest, InferenceResponse, InferenceResult

app = FastAPI()

# Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

@app.post("/register", status_code=201)
async def register_worker(worker: Worker):
    """Registers a new worker."""
    redis_client.set(f"worker:{worker.worker_id}", worker.model_dump_json())
    return {"message": "Worker registered successfully", "worker_id": worker.worker_id}

@app.get("/workers", response_model=List[Worker])
async def get_workers() -> List[Worker]:
    """Returns a list of all registered workers."""
    workers = []
    for key in redis_client.scan_iter("worker:*"):
        worker_data = redis_client.get(key)
        if worker_data:
            workers.append(Worker.model_validate_json(worker_data))
    return workers

@app.post("/inference", response_model=InferenceResponse)
async def create_inference_job(request: InferenceRequest):
    """Creates a new inference job and queues it for a worker."""
    # Find a worker that supports the requested model
    all_workers = []
    for key in redis_client.scan_iter("worker:*"):
        worker_data = redis_client.get(key)
        if worker_data:
            all_workers.append(Worker.model_validate_json(worker_data))
    
    compatible_workers = [
        worker
        for worker in all_workers
        if request.model in worker.supported_models
    ]

    if not compatible_workers:
        raise HTTPException(status_code=400, detail="No available worker for the requested model")

    # Use a round-robin strategy to select a worker
    worker_index = redis_client.incr("worker_index") % len(compatible_workers)
    target_worker = compatible_workers[worker_index]

    request_id = str(uuid.uuid4())

    job = {
        "request_id": request_id,
        "model": request.model,
        "prompt": request.prompt,
        "params": request.params,
    }

    # Push the job to the worker's queue
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
