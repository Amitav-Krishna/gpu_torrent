# Inference Worker

The inference worker is a FastAPI application that performs the actual ML inference. It registers with the central coordinator, listens for jobs on a Redis queue, and executes them using a pre-trained model from the Hugging Face Hub.

**Note:** This worker currently uses a dummy inference function. To use a real model, you will need to install `transformers` and `torch` and modify the `src/worker/inference/inference.py` file.

## Installation

To install the necessary dependencies, run the following command:

```bash
pip install -r src/worker/requirements.txt
```

**Note:** `pynvml` requires the NVIDIA driver to be installed.

## Configuration

The worker is configured using the following environment variables:

| Variable          | Description                                         | Default                            |
| ----------------- | --------------------------------------------------- | ---------------------------------- |
| `COORDINATOR_URL` | The URL of the central coordinator.                 | `http://localhost:8000`            |
| `REDIS_URL`       | The URL of the Redis server.                        | `redis://localhost:6379`           |
| `MODEL_NAME`      | The name of the Hugging Face model to use.          | `meta-llama/Llama-2-7b-chat-hf` |

## Usage

To start the worker, run the following command:

```bash
uvicorn src.worker.main:app --host 0.0.0.0 --port 8001
```
