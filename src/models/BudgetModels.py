from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class BudgetDetails(BaseModel):
    description: str
    type: str
    date: str
    num_barmans: int
    num_guests: int
    time: float
    package: str
    extras: Optional[List[str]] = None
    
class BudgetDetailsUpdate(BaseModel):
    description: Optional[str] = None
    type: Optional[str] = None
    date: Optional[str] = None
    num_barmans: Optional[int] = None
    num_guests: Optional[int] = None
    time: Optional[float] = None
    package: Optional[str] = None
    extras: Optional[List[str]] = None
    
class BudgetIn(BaseModel):
    name: str
    email: str = Field(..., pattern=r"^.+@.+\..+$")
    phone: str
    budget: BudgetDetails
    status: str = "Pendente"
    
class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    email: str = Field(..., pattern=r"^.+@.+\..+$")
    phone: Optional[str] = None
    budget: Optional[BudgetDetailsUpdate] = None

class Budget(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    phone: str
    budget: BudgetDetails
    status: str