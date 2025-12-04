import asyncio
from src.client.api import APIClient
from src.client.models import InferenceRequest

async def main():
    """
    Submits an inference job and retrieves the result.
    """
    client = APIClient(base_url="http://localhost:8000")

    request = InferenceRequest(
        model="meta-llama/Llama-2-7b-chat-hf",
        prompt="What is the capital of France?",
        params={}
    )

    response = await client.submit_inference_job(request)
    if response:
        print(f"Submitted job with request ID: {response.request_id}")
        result = await client.get_result(response.request_id)
        if result:
            print(f"Received result: {result.result}")
        else:
            print("Failed to retrieve result.")

if __name__ == "__main__":
    asyncio.run(main())
