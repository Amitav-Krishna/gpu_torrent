# Central Coordinator

The central coordinator is a FastAPI application that manages a fleet of ML inference workers. It is responsible for worker registration, job queuing, and result retrieval.

## Features

| Feature                 | Implementation                                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Worker Registration** | `POST /register`: Workers register themselves by sending their metadata to this endpoint. The coordinator stores this data in Redis.      |
| **Worker Discovery**    | `GET /workers`: Clients can retrieve a list of all registered workers.                                                                      |
| **Job Queuing**         | `POST /inference`: Clients submit inference jobs to this endpoint. The coordinator finds a compatible worker and queues the job in Redis. |
| **Result Retrieval**    | `GET /result/{request_id}`: Clients can retrieve the results of an inference job by its ID.                                               |
| **Load Balancing**      | A simple round-robin strategy is implemented in the `/inference` endpoint to distribute jobs evenly across workers.                         |

## Production Readiness Checklist

Before this system is ready for production, the following items should be addressed:

-   **Authentication & Authorization:** Secure the API endpoints to prevent unauthorized access.
-   **HTTPS:** Enforce HTTPS to encrypt all communication.
-   **Robust Logging & Monitoring:** Implement a structured logging solution and integrate with a monitoring platform to track the health of the system.
-   **Scalability:**
    -   **Coordinator:** Deploy the coordinator in a way that it can be horizontally scaled.
    -   **Redis:** Use a managed Redis service or a clustered Redis setup for high availability and scalability.
-   **Error Handling:** Implement more comprehensive error handling and a strategy for retrying failed jobs.
-   **Worker Heartbeat:** Implement a mechanism for workers to periodically send a heartbeat to the coordinator. This will allow the coordinator to detect and remove stale or unresponsive workers from the registry.
-   **Configuration Management:** Use a more robust configuration management solution instead of relying solely on environment variables.
-   **End-to-End Testing:** Develop a comprehensive suite of end-to-end tests that simulate the entire workflow, from job submission to result retrieval.
-   **CI/CD:** Set up a CI/CD pipeline for automated testing and deployment.
