import httpx
import time
import asyncio
from typing import Optional

from src.client.models import InferenceRequest, InferenceResponse, InferenceResult

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def submit_inference_job(self, request: InferenceRequest) -> Optional[InferenceResponse]:
        """Submits an inference job to the coordinator."""
        try:
            response = await self.client.post(f"{self.base_url}/inference", json=request.model_dump())
            response.raise_for_status()
            return InferenceResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            print(f"Error submitting inference job: {e}")
            return None

    async def get_result(self, request_id: str, poll_interval: int = 5) -> Optional[InferenceResult]:
        """Retrieves the result of an inference job, polling until it's available."""
        while True:
            try:
                response = await self.client.get(f"{self.base_url}/result/{request_id}")
                if response.status_code == 200:
                    return InferenceResult.model_validate(response.json())
                elif response.status_code == 404:
                    print("Result not yet available, polling again...")
                    await asyncio.sleep(poll_interval)
                else:
                    response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"Error retrieving result: {e}")
                return None
            except asyncio.CancelledError:
                print("Polling cancelled.")
                break
