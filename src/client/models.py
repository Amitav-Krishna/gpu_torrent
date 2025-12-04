from pydantic import BaseModel
from typing import Dict, Any

class InferenceRequest(BaseModel):
    model: str
    prompt: str
    params: Dict[str, Any]

class InferenceResponse(BaseModel):
    request_id: str
    message: str

class InferenceResult(BaseModel):
    request_id: str
    result: Dict
