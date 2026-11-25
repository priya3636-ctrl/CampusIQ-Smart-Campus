from sqlalchemy import text
from sqlalchemy.orm import Session
from langchain_ollama import OllamaEmbeddings

EMBEDDING_MODEL = "all-minilm"


def retrieve_documents(
    db: Session,
    question: str,
    limit: int = 3
) -> list[dict]:

    if not question.strip():
        return []

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    query_vector = embeddings.embed_query(question)

    sql = text("""
        SELECT
            id,
            title,
            source,
            content,
            embedding <=> CAST(:query_vector AS vector) AS distance
        FROM campus_documents
        ORDER BY embedding <=> CAST(:query_vector AS vector)
        LIMIT :limit
    """)

    rows = db.execute(
        sql,
        {
            "query_vector": str(query_vector),
            "limit": limit
        }
    ).mappings().all()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "source": row["source"],
            "content": row["content"],
            "distance": float(row["distance"])
        }
        for row in rows
    ]