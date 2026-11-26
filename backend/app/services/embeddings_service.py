
import os

from langchain_huggingface import HuggingFaceEndpointEmbeddings


def get_embeddings():
    token = os.getenv("HF_TOKEN")

    if not token:
        raise ValueError("HF_TOKEN is not configured.")

    return HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=token
    )
