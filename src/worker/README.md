# GPU Worker Node

This document outlines the implementation of the GPU worker node, which is responsible for registering with the coordinator and performing inference tasks.

## Architecture

The worker is a FastAPI application that, on startup, gathers information about the host's GPU and sends it to the coordinator's `/register` endpoint. This information includes the GPU model, VRAM, and a list of supported models.

The worker uses the `nvidia-ml-py` library to dynamically gather GPU specifications. It includes error handling to gracefully manage scenarios where the NVIDIA driver or `pynvml` library are not available, in which case it will register with placeholder data.

The worker communicates with the coordinator over HTTP using the `httpx` library for asynchronous requests.

## Code Structure

- `main.py`: The main entry point for the worker application. It contains the FastAPI application, the worker registration logic, and the GPU specification gathering logic.
- `requirements.txt`: A list of the Python dependencies required by the worker.
- `README.md`: This document.

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

## Future Improvements

- **Multi-GPU support:** The current implementation only supports the first GPU (`index 0`). Future versions could be extended to support multiple GPUs.
- **Configurable supported models:** The list of supported models is currently hardcoded. This could be made configurable through an environment variable or a configuration file.
- **Health checks:** The worker should expose a health check endpoint that the coordinator can use to monitor the worker's status.
