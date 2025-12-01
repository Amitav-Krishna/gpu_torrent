import asyncio
import json
import redis.asyncio as redis

async def get_result(request_id: str, redis_url: str):
    """
    Connects to Redis and retrieves a result from a result-specific queue.
    """
    try:
        redis_client = await redis.from_url(redis_url)
        queue_name = f"results:{request_id}"
        print(f"Client subscribing to queue: {queue_name}")

        # Wait for a result to be pushed to the queue
        _, result_payload = await redis_client.blpop(queue_name)
        result_data = json.loads(result_payload)

        print(f"Received result: {result_data}")
        return result_data

    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        return None
    finally:
        if 'redis_client' in locals() and redis_client:
            await redis_client.close()

if __name__ == '__main__':
    # Example usage
    async def main():
        request_id = "some_request_id"  # Replace with a real request_id
        redis_url = "redis://localhost:6379"

        # In a real scenario, you would first submit a job and get a request_id
        # For this example, we'll assume a result is pushed manually to Redis
        # for testing purposes.

        # You can test this by running:
        # redis-cli
        # > LPUSH results:some_request_id '{"text": "example result"}'

        result = await get_result(request_id, redis_url)
        if result:
            print(f"Result for request {request_id}: {result}")

    asyncio.run(main())
