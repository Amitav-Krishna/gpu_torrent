# Client-Side Result Retrieval

This document outlines the client-side mechanism for retrieving inference job results from the distributed worker system.

## Architecture

The client is responsible for retrieving the results of previously submitted inference jobs. The communication between the worker and the client is facilitated by a Redis queue.

When a worker finishes processing a job, it pushes the result to a Redis list specific to that job's request ID. The client can then connect to Redis and retrieve the result from this list.

## Code Structure

-   `results.py`: Contains the core function `get_result`, which blocks and waits for a result to be available in the specified Redis queue.
-   `test_results.py`: An end-to-end integration test that demonstrates how to submit a job and retrieve its result.
-   `README.md`: This document.

## Usage

To retrieve a result, import and call the `get_result` function with the `request_id` of the job and the Redis URL.

```python
import asyncio
from src.client.results import get_result

async def main():
    request_id = "your-request-id"
    redis_url = "redis://localhost:6379"

    result = await get_result(request_id, redis_url)
    if result:
        print(f"Retrieved result: {result}")
    else:
        print("Failed to retrieve result.")

if __name__ == "__main__":
    asyncio.run(main())
```

## Future Improvements for Production

The current implementation provides a basic, functional demonstration. For a production-ready system, the following areas should be addressed:

-   **Robust Error Handling & Timeouts:**
    -   The `get_result` function currently blocks indefinitely. If a worker fails and never returns a result, the client will hang. A timeout mechanism is critical.
    -   A standardized error format should be implemented so workers can report failures (e.g., model loading errors, inference exceptions) back to the client via the results queue.

-   **Efficient Connection Management:**
    -   The current `get_result` function establishes a new Redis connection for every call. This is inefficient for clients that need to retrieve many results. A long-lived, shared Redis connection or a connection pool should be implemented to reduce overhead.

-   **Security:**
    -   The connection to Redis is currently unsecured. In a production environment, Redis should be configured with password authentication (e.g., `redis://:password@localhost:6379`).
    -   For sensitive data, the communication should be encrypted using SSL/TLS.

-   **Alternative Communication Patterns:**
    -   While `BLPOP` is efficient, some client architectures may benefit from a push-based model. Future versions could include support for webhooks, where the worker actively pushes the result to a client-specified HTTP endpoint, or WebSockets for real-time, bidirectional communication.

-   **Abstracted Client SDK:**
    -   The logic for both submitting a job and retrieving its result could be encapsulated into a more polished, user-friendly client SDK. This would abstract away the direct Redis interactions and provide a simpler API for developers.
