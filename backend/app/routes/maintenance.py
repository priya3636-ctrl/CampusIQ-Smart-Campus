
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from uuid import uuid4

Session = Any

from app.database import get_db
from app import models, schemas
from app.agents.complaint_prioritizer import prioritize_complaint


router = APIRouter(
    prefix="/api/maintenance",
    tags=["Maintenance Management"]
)


# ==========================================
# 1. CREATE MAINTENANCE REQUEST
# ==========================================

@router.post(
    "/",
    response_model=schemas.MaintenanceRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_maintenance_request(
    request: schemas.MaintenanceRequestCreate,
    db: Session = Depends(get_db)
):
    new_request = models.MaintenanceRequest(
        request_code=f"REQ-{uuid4().hex[:8].upper()}",
        title=request.title.strip(),
        location=request.location.strip(),
        category=request.category,
        priority=request.priority,
        description=request.description.strip(),
        status="Pending"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


# ==========================================
# 2. GET ALL MAINTENANCE REQUESTS
# ==========================================

@router.get(
    "/",
    response_model=List[schemas.MaintenanceRequestResponse]
)
def get_all_maintenance_requests(
    db: Session = Depends(get_db)
):
    requests = (
        db.query(models.MaintenanceRequest)
        .order_by(models.MaintenanceRequest.created_at.desc())
        .all()
    )

    return requests


# ==========================================
# 3. DASHBOARD ANALYTICS
# ==========================================

@router.get("/stats")
def get_maintenance_stats(
    db: Session = Depends(get_db)
):
    total_requests = db.query(
        models.MaintenanceRequest
    ).count()

    pending_requests = db.query(
        models.MaintenanceRequest
    ).filter(
        models.MaintenanceRequest.status == "Pending"
    ).count()

    high_priority_requests = db.query(
        models.MaintenanceRequest
    ).filter(
        models.MaintenanceRequest.priority.in_(["High", "Critical"])
    ).count()

    category_data = db.query(
        models.MaintenanceRequest.category,
        func.count(models.MaintenanceRequest.id)
    ).group_by(
        models.MaintenanceRequest.category
    ).all()

    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "high_priority_requests": high_priority_requests,

        "in_progress_requests": db.query(
            models.MaintenanceRequest
        ).filter(
            models.MaintenanceRequest.status == "In Progress"
        ).count(),

        "resolved_requests": db.query(
            models.MaintenanceRequest
        ).filter(
            models.MaintenanceRequest.status == "Resolved"
        ).count(),

        "category_breakdown": [
            {
                "category": category,
                "count": count
            }
            for category, count in category_data
        ]
    }
# ==========================================
# 4. GET ONE MAINTENANCE REQUEST
# ==========================================

@router.get(
    "/{request_id}",
    response_model=schemas.MaintenanceRequestResponse
)
def get_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    request = (
        db.query(models.MaintenanceRequest)
        .filter(models.MaintenanceRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Maintenance request not found"
        )

    return request


# ==========================================
# 5. UPDATE REQUEST STATUS
# ==========================================

@router.patch(
    "/{request_id}/status",
    response_model=schemas.MaintenanceRequestResponse
)
def update_maintenance_status(
    request_id: int,
    update: schemas.MaintenanceStatusUpdate,
    db: Session = Depends(get_db)
):
    request = (
        db.query(models.MaintenanceRequest)
        .filter(models.MaintenanceRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Maintenance request not found"
        )

    allowed_statuses = ["Pending", "In Progress", "Resolved"]

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Choose Pending, In Progress, or Resolved."
        )

    request.status = update.status

    db.commit()
    db.refresh(request)

    return request


# ==========================================
# 6. DELETE MAINTENANCE REQUEST
# ==========================================

@router.delete("/{request_id}")
def delete_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    request = (
        db.query(models.MaintenanceRequest)
        .filter(models.MaintenanceRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Maintenance request not found"
        )

    db.delete(request)
    db.commit()

    return {
        "message": "Maintenance request deleted successfully"
    }


# ==========================================
# 7. AI COMPLAINT PRIORITIZATION
# ==========================================

@router.post("/analyze")
def analyze_maintenance_complaint(
    request: schemas.MaintenanceRequestCreate
):
    analysis = prioritize_complaint(
        title=request.title,
        description=request.description,
        category=request.category
    )

    return {
        "project": "CampusIQ",
        "agent": "Complaint Prioritizer",
        "analysis": analysis
    }
