import asyncio
import json
import uuid
import redis.asyncio as redis
from src.client.results import get_result

async def submit_job(redis_client, worker_id: str, request_id: str):
    """
    Submits a dummy job to the worker's queue.
    """
    queue_name = f"worker:{worker_id}"
    job_data = {
        "request_id": request_id,
        "model": "dummy_model",
        "prompt": "This is a test prompt.",
        "params": {}
    }
    await redis_client.lpush(queue_name, json.dumps(job_data))
    print(f"Submitted job {request_id} to {queue_name}")

async def main():
    """
    Submits a job and then retrieves the result.
    """
    worker_id = "test_worker"  # In a real system, this would be dynamically assigned
    request_id = str(uuid.uuid4())
    redis_url = "redis://localhost:6379"

    redis_client = await redis.from_url(redis_url)

    # Submit a job
    await submit_job(redis_client, worker_id, request_id)

    # Retrieve the result
    result = await get_result(request_id, redis_url)

    if result:
        print(f"Test passed! Result for request {request_id}: {result}")
    else:
        print(f"Test failed! No result received for request {request_id}")

    await redis_client.close()

if __name__ == "__main__":
    # To run this test, you need to have a worker running with the ID "test_worker"
    # You can modify the worker's main.py to use a fixed worker_id for testing.
    asyncio.run(main())
