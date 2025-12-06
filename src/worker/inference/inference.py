import ollama


async def execute_inference(model: str, prompt: str, params: dict) -> dict:
    """
    Executes inference using an Ollama model and returns the response.
    """
    print(f"Executing inference for model {model} with prompt: {prompt[:50]}...")

    options = {}
    if "temperature" in params:
        options["temperature"] = params["temperature"]
    if "num_predict" in params:
        options["num_predict"] = params["num_predict"]
    if "top_p" in params:
        options["top_p"] = params["top_p"]
    if "top_k" in params:
        options["top_k"] = params["top_k"]

    response = await ollama.AsyncClient().generate(
        model=model,
        prompt=prompt,
        options=options if options else None,
    )

    return {"text": response["response"]}
