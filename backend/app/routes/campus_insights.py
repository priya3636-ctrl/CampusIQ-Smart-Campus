
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.campus_graph import analyze_campus

router = APIRouter(
    prefix="/api/campus",
    tags=["Campus AI Insights"]
)


class CampusAnalysisRequest(BaseModel):
    feedback: Optional[str] = ""
    resources: Optional[str] = ""
    energy: Optional[str] = ""
    schedule: Optional[str] = ""
    campus_data: Optional[str] = ""
    maintenance_title: Optional[str] = ""
    maintenance_description: Optional[str] = ""
    maintenance_category: Optional[str] = "General"


@router.post("/analyze")
def analyze_campus_insights(request: CampusAnalysisRequest):
    data = request.model_dump()

    if not any(
        value.strip()
        for value in data.values()
        if isinstance(value, str)
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide campus information."
        )

    try:
        return analyze_campus(data)
    except Exception as error:
        print(f"Campus Insights API error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Campus analysis could not be completed."
        )
