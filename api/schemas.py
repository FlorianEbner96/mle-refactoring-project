"""Pydantic schemas: the validated request and response shapes of the API."""

from pydantic import BaseModel, ConfigDict, Field


class HouseBase(BaseModel):
    """The five house features shared by every request and response."""

    bedrooms: int = Field(ge=0, le=20)
    bathrooms: float = Field(ge=0, le=20)
    sqft_living: int = Field(ge=100)
    grade: int = Field(ge=1, le=13)
    zipcode: str = Field(min_length=5, max_length=10)


class HouseCreate(HouseBase):
    """Request body for creating a house."""


class HouseUpdate(HouseBase):
    """Request body for replacing a house."""


class HouseOut(HouseBase):
    """Response body: the five features plus the database id."""

    model_config = ConfigDict(from_attributes=True)

    id: int
