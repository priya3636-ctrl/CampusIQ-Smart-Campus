
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Data received from the frontend
class MaintenanceRequestCreate(BaseModel):

    title: str = Field(min_length=3, max_length=200)

    location: str = Field(min_length=2, max_length=150)

    category: str = Field(min_length=2, max_length=100)

    priority: Literal["Low", "Medium", "High"]

    description: str = Field(min_length=5, max_length=2000)


# Data used when updating request status
class MaintenanceStatusUpdate(BaseModel):

    status: Literal["Pending", "In Progress", "Resolved"]


# Data returned to the frontend
class MaintenanceRequestResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    request_code: str

    title: str

    location: str

    category: str

    priority: str

    description: str

    status: str

    created_at: datetime
