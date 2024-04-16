from loguru import logger

import torch
from llama_index.core.callbacks import LlamaDebugHandler, CallbackManager
from llama_index.llms.huggingface import HuggingFaceLLM


def get_llm(
    model_name: str = None,
    tokenizer_name: str = None,
    context_window: int = None,
    max_new_tokens: int = None,
    temperature: float = None,
):
    if not context_window:
        context_window = 2048

    if not max_new_tokens:
        max_new_tokens = 256

    if not temperature:
        temperature = 0.5

    if not model_name:
        logger.warning("Model not setted, will use default model")
        model_name = "StabilityAI/stablelm-tuned-alpha-3b"
        # model_name = "TheBloke/TinyLlama-1.1B-Chat-v0.3-GPTQ"
    if not tokenizer_name:
        if model_name:
            tokenizer_name = model_name
        else:
            tokenizer_name = "StabilityAI/stablelm-tuned-alpha-3b"
            # tokenizer_name = "TheBloke/TinyLlama-1.1B-Chat-v0.3-GPTQ"

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])

    return HuggingFaceLLM(
        context_window=context_window,
        max_new_tokens=max_new_tokens,
        generate_kwargs={"temperature": temperature, "do_sample": True},
        tokenizer_name=tokenizer_name,
        model_name=model_name,
        device_map="auto",
        callback_manager=callback_manager,
        tokenizer_kwargs={"max_length": 4096},
        # change these settings below depending on your GPU
        # model_kwargs={"torch_dtype": torch.float16, "load_in_8bit": False},
    )
