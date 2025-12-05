# Inference Worker

The inference worker is a FastAPI application that performs the actual ML inference. It registers with the central coordinator, listens for jobs on a Redis queue, and executes them using a pre-trained model from the Hugging Face Hub.

**Note:** This worker currently uses a dummy inference function. To use a real model, you will need to install `transformers` and `torch` and modify the `src/worker/inference/inference.py` file.

## Prerequisites

- **Redis server**: Must be running on the coordinator machine (not on the worker). The worker connects to Redis via `REDIS_URL`.
- **NVIDIA driver**: Required for `pynvml` to detect GPU specs. Without it, the worker will register with placeholder GPU info.

## Installation

To install the necessary dependencies, run the following command:

```bash
pip install -r src/worker/requirements.txt
```

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

## Usage

To start the worker, run the following command:

```bash
uvicorn src.worker.main:app --host 0.0.0.0 --port 8001
```
