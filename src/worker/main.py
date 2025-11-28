import httpx
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://localhost:8000")

class WorkerRegistration(BaseModel):
    gpu_model: str
    vram: float # in GB
    supported_models: List[str]

import pynvml

def get_gpu_specs() -> WorkerRegistration:
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
            gpu_model=gpu_model,
            vram=round(vram, 2),
            supported_models=["meta-llama/Llama-2-7b-chat-hf", "mistralai/Mistral-7B-v0.1"]
        )
    except pynvml.NVMLError:
        print("pynvml is not installed or failed to initialize. Using placeholder data.")
        return WorkerRegistration(
            gpu_model="N/A",
            vram=0.0,
            supported_models=[]
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Registers the worker with the coordinator on startup.
    """
    worker_specs = get_gpu_specs()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{COORDINATOR_URL}/register", json=worker_specs.model_dump())
            response.raise_for_status()
        print("Worker registered successfully.")
    except httpx.RequestError as e:
        print(f"Failed to register worker: {e}")
    yield

app = FastAPI(lifespan=lifespan)
