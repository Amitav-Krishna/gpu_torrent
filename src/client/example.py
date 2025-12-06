import asyncio

from src.client.api import APIClient
from src.client.models import InferenceRequest

async def main():
    """
    Submits an inference job and retrieves the result.
    """
    client = APIClient(base_url="http://localhost:8000")

    # Create an inference request
    request = InferenceRequest(
        model="llama3.2",
        prompt="Give me a recipe for an eggless chocolate cake.",
        params={},
    )

    # Submit the job
    response = await client.submit_inference_job(request)
    if not response:
        return

    print(f"Submitted job with request ID: {response.request_id}")

    # Retrieve the result
    result = await client.get_result(response.request_id)
    if not result:
        return

    print(f"Received result: {result.result}")

if __name__ == "__main__":
    asyncio.run(main())
