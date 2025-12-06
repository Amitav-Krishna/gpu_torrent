import asyncio
import json
import redis.asyncio as redis
import uuid
from ..inference import inference

async def redis_consumer(worker_id: str, redis_url: str):
    """
    Connects to Redis, subscribes to a worker-specific queue, and processes inference jobs.
    """
    try:
        redis_client = await redis.from_url(redis_url)
        queue_name = f"queue:{worker_id}"
        print(f"Worker {worker_id} subscribing to queue: {queue_name}")

        while True:
            try:
                # RPOP returns a tuple of (queue_name, item)
                _, job_payload = await redis_client.brpop(queue_name)
                job_data = json.loads(job_payload)

                print(f"Received job: {job_data['request_id']}")

                result = await inference.execute_inference(
                    job_data["model"],
                    job_data["prompt"],
                    job_data["params"]
                )

                result_key = f"result:{job_data['request_id']}"
                result_data = {"request_id": job_data['request_id'], "result": result}
                await redis_client.set(result_key, json.dumps(result_data))
                print(f"Finished job: {job_data['request_id']}, result sent to {result_key}")

            except json.JSONDecodeError:
                print("Error: Invalid JSON payload")
            except Exception as e:
                print(f"An error occurred: {e}")

    except redis.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
    finally:
        if 'redis_client' in locals() and redis_client:
            await redis_client.close()

if __name__ == '__main__':
    # Example usage
    worker_id = str(uuid.uuid4())
    redis_url = "redis://localhost:6379"
    asyncio.run(redis_consumer(worker_id, redis_url))
