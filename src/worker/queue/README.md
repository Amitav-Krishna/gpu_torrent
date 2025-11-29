# Worker Queue Consumer

This document defines the interface for the worker's Redis queue consumer.

## Queue Naming Convention

Each worker subscribes to a unique Redis queue named `worker:<worker_id>`, where `<worker_id>` is a unique identifier for the worker.

## Job Payload Format

The job payload is a JSON string with the following format:

```json
{
  "request_id": "string",
  "model": "string",
  "prompt": "string",
  "params": {
    "temperature": "float",
    "max_tokens": "int"
  }
}
```

-   `request_id`: A unique identifier for the inference request.
-   `model`: The name of the model to use for inference.
-   `prompt`: The input text for the model.
-   `params`: A dictionary of parameters for the vLLM engine.
