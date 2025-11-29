import httpx
import os
import asyncio
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from .queue.consumer import redis_consumer

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://localhost:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class WorkerRegistration(BaseModel):
    worker_id: str
    gpu_model: str
    vram: float # in GB
    supported_models: List[str]

import pynvml

def get_gpu_specs(worker_id: str) -> WorkerRegistration:
    """
    Gathers GPU specifications using pynvml.
    """
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_model = pynvml.nvmlDeviceGetName(handle)
        vram = pynvml.nvmlDeviceGetMemoryInfo(handle).total / 1024**3
        pynvml.nvmlShutdown()

        return WorkerRegistration(
            worker_id=worker_id,
            gpu_model=gpu_model,
            vram=round(vram, 2),
            supported_models=["meta-llama/Llama-2-7b-chat-hf", "mistralai/Mistral-7B-v0.1"]
        )
    except pynvml.NVMLError:
        print("pynvml is not installed or failed to initialize. Using placeholder data.")
        return WorkerRegistration(
            worker_id=worker_id,
            gpu_model="N/A",
            vram=0.0,
            supported_models=[]
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Registers the worker with the coordinator on startup and starts the Redis consumer.
    """
    worker_id = str(uuid.uuid4())
    consumer_task = asyncio.create_task(redis_consumer(worker_id, REDIS_URL))

    worker_specs = get_gpu_specs(worker_id)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{COORDINATOR_URL}/register", json=worker_specs.model_dump())
            response.raise_for_status()
        print("Worker registered successfully.")
    except httpx.RequestError as e:
        print(f"Failed to register worker: {e}")

    yield

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("Redis consumer task cancelled.")

app = FastAPI(lifespan=lifespan)
