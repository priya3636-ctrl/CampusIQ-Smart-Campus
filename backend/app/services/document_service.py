
from time import perf_counter

from sqlalchemy.orm import Session

from app.models import CampusDocument


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


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

    documents = []

    for index, chunk in enumerate(chunks):
        documents.append(
            CampusDocument(
                title=title.strip(),
                source=source.strip(),
                content=chunk,
                chunk_index=index,
                embedding=None
            )
        )

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
