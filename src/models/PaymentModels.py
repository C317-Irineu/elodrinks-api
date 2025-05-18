from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any

class Item(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: Optional[str] = None
    quantity: int
    currency_id: Optional[str] = None
    unit_price: float
    
class BackUrls(BaseModel):
    success: str
    failure: str
    pending: str

class PaymentPreference(BaseModel):
    items: List[Item]
    payer: Optional[Dict[str, Any]] = None
    notification_url: Optional[HttpUrl] = None
    external_reference: Optional[str] = None
    binary_mode: bool = False
    back_urls: Optional[BackUrls] = None
    auto_return: Optional[str] = None