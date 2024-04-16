import torch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_embed_model(model_name: str = None, device: str = None):
    if not model_name:
        model_name = "BAAI/bge-small-en-v1.5"
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    return HuggingFaceEmbedding(
        model_name=model_name, cache_folder="./models", device=device
    )
