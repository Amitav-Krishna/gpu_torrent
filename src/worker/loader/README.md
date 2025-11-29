# Model Loader

This component is responsible for loading a specified model into VRAM on worker startup.

## Usage

To use the model loader, import the `load_model` function from `model_loader.py` and call it with the desired model name.

```python
from .loader import model_loader

model = model_loader.load_model("my-model")
```

## Future Improvements

- **Lazy loading:** Instead of loading the model on startup, it could be loaded on the first request.
- **Model unloading:** The model could be unloaded from VRAM after a period of inactivity to free up resources.
- **Model caching:** The model could be cached on disk to speed up loading times.
- **Error handling:** The model loader could be made more robust by adding error handling for cases where the model fails to load.
