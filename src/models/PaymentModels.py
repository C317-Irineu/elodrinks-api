from pydantic import BaseModel, Field
from typing import List, Optional

class Item(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: Optional[str] = None
    quantity: int
    currency_id: Optional[str] = None
    unit_price = float

class PaymentPreferenceCreate(BaseModel):
    items: List[Item]
    payer: Optional[str] = None
    notification_url: Optional[str] = None
    external_reference: Optional[str] = None
    binary_mode: bool = False