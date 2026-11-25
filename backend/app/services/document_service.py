
from functools import lru_cache
from time import perf_counter

from langchain_ollama import OllamaEmbeddings
from sqlalchemy.orm import Session

from app.models import CampusDocument


# Local embedding model
EMBEDDING_MODEL = "all-minilm"

# Chunk configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


@lru_cache(maxsize=1)
def get_embeddings():
    """Reuse one embedding client instead of creating it for every upload."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL)


def split_text(text: str) -> list[str]:
    """Split a document into smaller overlapping text chunks."""

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def ingest_document(
    db: Session,
    title: str,
    source: str,
    content: str
) -> dict:
    """Generate embeddings and save document chunks in PostgreSQL."""

    total_start = perf_counter()

    if not title.strip():
        raise ValueError("Document title cannot be empty.")

    if not source.strip():
        raise ValueError("Document source cannot be empty.")

    if not content.strip():
        raise ValueError("Document content cannot be empty.")

    chunks = split_text(content)

    if not chunks:
        raise ValueError("No readable text found in the document.")

    print(f"Document chunks created: {len(chunks)}")

    # Generate embeddings
    embedding_start = perf_counter()

    embeddings = get_embeddings()
    vectors = embeddings.embed_documents(chunks)

    embedding_time = perf_counter() - embedding_start

    print(f"Embedding generation time: {embedding_time:.2f} seconds")

    if len(vectors) != len(chunks):
        raise ValueError("Embedding count does not match chunk count.")

    documents = []

    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):

        if len(vector) != 384:
            raise ValueError(
                f"Expected 384 embedding dimensions, received {len(vector)}."
            )

        documents.append(
            CampusDocument(
                title=title.strip(),
                source=source.strip(),
                content=chunk,
                chunk_index=index,
                embedding=vector
            )
        )

    # Save to database
    database_start = perf_counter()

    try:
        db.add_all(documents)
        db.commit()

    except Exception:
        db.rollback()
        raise

    database_time = perf_counter() - database_start
    total_time = perf_counter() - total_start

    print(f"Database save time: {database_time:.2f} seconds")
    print(f"Total document processing time: {total_time:.2f} seconds")

    return {
        "status": "success",
        "title": title,
        "source": source,
        "chunks_created": len(chunks),
        "chunks_stored": len(documents),
        "processing_time_seconds": round(total_time, 2)
    }
