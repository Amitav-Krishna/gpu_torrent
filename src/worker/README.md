# GPU Worker Node

This document outlines the implementation of the GPU worker node, which is responsible for registering with the coordinator and performing inference tasks.

## Architecture

<<<<<<< HEAD
## Prerequisites

- **Redis server**: Must be running on the coordinator machine (not on the worker). The worker connects to Redis via `REDIS_URL`.
- **NVIDIA driver**: Required for `pynvml` to detect GPU specs. Without it, the worker will register with placeholder GPU info.

## Installation
=======
The worker is a FastAPI application that, on startup, gathers information about the host's GPU and sends it to the coordinator's `/register` endpoint. This information includes the GPU model, VRAM, and a list of supported models.
>>>>>>> e7d80e7 (I don't know bro)

The worker uses the `nvidia-ml-py` library to dynamically gather GPU specifications. It includes error handling to gracefully manage scenarios where the NVIDIA driver or `pynvml` library are not available, in which case it will register with placeholder data.

The worker communicates with the coordinator over HTTP using the `httpx` library for asynchronous requests.

<<<<<<< HEAD
## Configuration

The worker is configured using the following environment variables:

| Variable          | Description                                         | Default                            |
| ----------------- | --------------------------------------------------- | ---------------------------------- |
| `COORDINATOR_URL` | The URL of the central coordinator.                 | `http://localhost:8000`            |
| `REDIS_URL`       | The URL of the Redis server (on coordinator).       | `redis://localhost:6379`           |
| `MODEL_NAME`      | The name of the Hugging Face model to use.          | `gpt2`                             |

### Using Gated Models (e.g., Llama-2)

Some models like `meta-llama/Llama-2-7b-chat-hf` are gated and require authentication:

1. Create a HuggingFace account at https://huggingface.co
2. Request access to the model (e.g., https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
3. Create an access token at https://huggingface.co/settings/tokens
4. Login via CLI:
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```

Alternatively, set the `HF_TOKEN` environment variable:
```bash
export HF_TOKEN="your_token_here"
```
=======
## Code Structure

- `main.py`: The main entry point for the worker application. It contains the FastAPI application, the worker registration logic, and the GPU specification gathering logic.
- `requirements.txt`: A list of the Python dependencies required by the worker.
- `README.md`: This document.
>>>>>>> e7d80e7 (I don't know bro)

## Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the worker:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```
   * Replace `8001` with the desired port number.

## Configuration

The following environment variables can be used to configure the worker:

- `COORDINATOR_URL`: The URL of the coordinator. Defaults to `http://localhost:8000`.

## Future Improvements for Scalability

To make this worker production-ready and scalable, the following areas should be addressed:

- **Robust Registration and Heartbeating:**
  - **Retry Mechanism:** The current registration is a one-time attempt on startup. A robust implementation should include a retry loop with exponential backoff to handle cases where the coordinator is temporarily unavailable.
  - **Heartbeating:** The worker should periodically send a heartbeat to the coordinator to signal that it is still alive and available to take tasks. If the coordinator misses a certain number of heartbeats, it should de-register the worker.

- **Structured Logging:**
  - The current use of `print()` statements is not suitable for production. It should be replaced with a structured logging library (e.g., Python's `logging` module configured to output JSON). This allows for easier parsing, searching, and monitoring in a centralized logging system (like the ELK stack or Splunk).

- **Containerization:**
  - A `Dockerfile` should be created for the worker. This will allow for consistent, reproducible deployments and is a prerequisite for scaling with container orchestration platforms.
  - **Orchestration:** For true scalability, the worker should be deployed and managed by a system like Kubernetes, which can automatically handle scaling, restarts, and service discovery.

- **Dynamic Model Management:**
  - The list of `supported_models` is currently hardcoded. A more scalable design would involve the worker dynamically loading or unloading models based on instructions from the coordinator. This would allow for more flexible resource management and prevent the worker from holding large models in memory unnecessarily.

- **Multi-GPU Support:**
  - The current implementation only supports the first GPU (`index 0`). Future versions could be extended to either report on all GPUs in a system or even manage multiple vLLM instances, one for each GPU.

- **Health Checks:**
  - The worker should expose a `/health` endpoint that the coordinator (or an orchestrator like Kubernetes) can use to verify the worker's status. This is critical for automated recovery and load balancing.
