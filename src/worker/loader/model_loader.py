import logging
import ollama

logging.basicConfig(level=logging.INFO)


def load_model(model_name: str):
    """
    Ensures an Ollama model is available locally, pulling it if necessary.

    Args:
        model_name: The name of the Ollama model to load (e.g., "llama3.2", "mistral").

    Returns:
        The model name if successful.
    """
    try:
        logging.info(f"Checking if model is available: {model_name}")
        models = ollama.list()
        model_names = [m.model for m in models.models]

        # Check if model is already available (with or without :latest tag)
        if model_name in model_names or f"{model_name}:latest" in model_names:
            logging.info(f"Model already available: {model_name}")
            return model_name

        logging.info(f"Pulling model: {model_name}")
        ollama.pull(model_name)
        logging.info(f"Model pulled successfully: {model_name}")
        return model_name
    except Exception as e:
        logging.error(f"Failed to load model: {model_name}", exc_info=e)
        raise
