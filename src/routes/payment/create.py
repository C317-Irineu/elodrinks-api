from fastapi import APIRouter, HTTPException
from src.models.PaymentModels import PaymentPreference
from src.services.payment.create import create_payment_preference

router = APIRouter(prefix="/payment",tags=["payment"])

@router.post("/", status_code=201, response_model=dict)
def create_payment(pref: PaymentPreference):
    try:
        result = create_payment_preference(pref)
        return {
            "preference_id": result.get("id"),
            "init_point": result.get("init_point"),
            "sandbox_init_point": result.get("sandbox_init_point"),
            "back_urls": result.get("back_urls"),
            "auto_return": result.get("auto_return"),
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    