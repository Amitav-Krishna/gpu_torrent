# Distributed Inference System

This project is a distributed inference system featuring a central coordinator, GPU workers, and a client for submitting jobs.

## Components

-   **Central Coordinator (`src/server`):** A FastAPI application that manages workers, queues inference jobs, and serves results.
-   **Inference Worker (`src/worker`):** A FastAPI application that registers with the coordinator, processes inference jobs using a Hugging Face model, and runs on a machine with a GPU. **Note:** This worker currently uses a dummy inference function.
-   **Client (`src/client`):** A Python library and example script for submitting inference jobs to the coordinator and retrieving results.

## Getting Started

To run the full end-to-end system, you'll need at least two machines on the same network: one to run the coordinator and Redis, and another to run the worker. You can run the client from either machine.

### Prerequisites

-   Python 3.8+
-   Redis
-   NVIDIA GPU with CUDA installed (for the worker)

### 1. Set up the Coordinator

On your first machine, follow these steps:

1.  **Install Redis:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y redis-server
    ```

2.  **Start Redis:**
    ```bash
    redis-server --daemonize yes
    ```

3.  **Install Coordinator Dependencies:**
    ```bash
    pip install -r src/server/requirements.txt
    ```

4.  **Start the Coordinator:**
    ```bash
    uvicorn src.server.main:app --host 0.0.0.0 --port 8000
    ```

### 2. Set up the Worker

On your second machine (with the GPU), follow these steps:

1.  **Install Worker Dependencies:**
    ```bash
    pip install -r src/worker/requirements.txt
    ```

2.  **Configure the Worker:**
    Set the following environment variables, replacing the placeholders with the appropriate values:

    ```bash
    export COORDINATOR_URL="http://<IP address of the coordinator machine>:8000"
    export REDIS_URL="redis://<IP address of the Redis machine>:6379"
    export MODEL_NAME="meta-llama/Llama-2-7b-chat-hf" # Or any other model
    ```

3.  **Start the Worker:**
    ```bash
    uvicorn src.worker.main:app --host 0.0.0.0 --port 8001
    ```

### 3. Run the Client

From either machine, you can now run the client to submit an inference job:

1.  **Install Client Dependencies:**
    ```bash
    pip install -r src/client/requirements.txt
    ```

2.  **Run the Example:**
    ```bash
    python -m src.client.example
    ```

This will submit a job to the coordinator, which will then be picked up by the worker. The client will poll for the result and print it to the console.
