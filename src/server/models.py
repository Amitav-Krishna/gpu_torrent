from pydantic import BaseModel
from typing import List, Dict

class Worker(BaseModel):
    worker_id: str
    gpu_info: Dict
    supported_models: List[str]

class InferenceRequest(BaseModel):
    model: str
    prompt: str
    params: Dict

class InferenceResponse(BaseModel):
    request_id: str
    message: str

class InferenceResult(BaseModel):
    request_id: str
    result: Dict
