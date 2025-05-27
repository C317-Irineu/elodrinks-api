from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class EmailDetails(BaseModel):
    email: str
    name: str
    type: str
    date: str
    value: str
    payment_link: str
    
class EmailIn(BaseModel):
    id: str = Field(alias="_id")