from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

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
    email: EmailStr
    phone: str
    budget: BudgetDetails
    status: str = "Pendente"
    value: Optional[float] = None
    
class BudgetUpdate(BaseModel):
    id: str = Field(alias="_id")
    new_status: str
    value: Optional[float] = None

class Budget(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    phone: str
    budget: BudgetDetails
    status: str
    value: Optional[float] = None