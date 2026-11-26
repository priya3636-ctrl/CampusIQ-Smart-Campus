from sqlalchemy import text
from sqlalchemy.orm import Session


def retrieve_documents(
    db: Session,
    question: str,
    limit: int = 3
) -> list[dict]:

    question = question.strip()

    if not question:
        return []

    sql = text("""
        WITH query AS (
            SELECT to_tsquery(
                'english',
                array_to_string(
                    tsvector_to_array(
                        to_tsvector('english', :question)
                    ),
                    ' | '
                )
            ) AS terms
        ),
        searchable_documents AS (
            SELECT
                id,
                title,
                source,
                content,
                created_at,
                to_tsvector(
                    'english',
                    coalesce(title, '') || ' ' ||
                    coalesce(source, '') || ' ' ||
                    coalesce(content, '')
                ) AS search_vector
            FROM campus_documents
        )
        SELECT
            id,
            title,
            source,
            content,
            ts_rank_cd(
                search_vector,
                query.terms
            ) AS score
        FROM searchable_documents, query
        WHERE search_vector @@ query.terms
        ORDER BY score DESC, created_at DESC
        LIMIT :limit
    """)

    rows = db.execute(
        sql,
        {
            "question": question,
            "limit": limit
        }
    ).mappings().all()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "source": row["source"],
            "content": row["content"],
            "score": float(row["score"])
        }
        for row in rows
    ]