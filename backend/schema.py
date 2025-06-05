from typing import Optional
from pydantic import BaseModel, Field

class ProspectInfo(BaseModel):
  """
  Key prospect details schema
  """
  name: str = Field(default=None, description="Prospect's full name")
  email: str = Field(default=None, description="Prospect's email address")
  phone: str = Field(default=None, description="10-digit phone number")

class BookTourInput(BaseModel):
    """
    Input schema for booking a tour
    """
    unit: int = Field(default=None, description="The ID of the unit to book a tour for")
    user_name: str = Field(default=None, description="The name of the user booking the tour")
    user_email: str = Field(default=None, description="The email of the user booking the tour")
    user_id: int = Field(default=None, description="The ID of the user who is booking the tour")