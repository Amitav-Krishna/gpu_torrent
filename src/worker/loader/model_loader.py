from transformers import AutoModelForCausalLM
import logging

logging.basicConfig(level=logging.INFO)

def load_model(model_name: str):
    """
    Loads a model from the Hugging Face Hub and returns the model object.

    Args:
        model_name: The name of the model to load.

    Returns:
        The loaded model object.
    """
    try:
        logging.info(f"Loading model: {model_name}")
        model = AutoModelForCausalLM.from_pretrained(model_name)
        logging.info(f"Model loaded successfully: {model_name}")
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {model_name}", exc_info=e)
        raise
