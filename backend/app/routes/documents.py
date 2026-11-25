
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.document_service import ingest_document

router = APIRouter(
    prefix="/api/documents",
    tags=["Campus Documents"]
)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a file."
        )

    filename = Path(file.filename).name

    if Path(filename).suffix.lower() != ".txt":
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported currently."
        )

    try:
        content_bytes = await file.read(MAX_FILE_SIZE + 1)

        if len(content_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 2 MB."
            )

        try:
            content = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Please upload a valid UTF-8 text file."
            )

        if not content.strip():
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        result = ingest_document(
            db=db,
            title=Path(filename).stem,
            source=filename,
            content=content
        )

        return {
            "message": "Document uploaded and processed successfully.",
            **result
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"Document Upload Error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check the backend terminal."
        )

    finally:
        await file.close()


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    from app.models import CampusDocument

    documents = (
        db.query(CampusDocument.title, CampusDocument.source)
        .distinct()
        .order_by(CampusDocument.title)
        .all()
    )

    return {
        "total_documents": len(documents),
        "documents": [
            {"title": item.title, "source": item.source}
            for item in documents
        ]
    }
