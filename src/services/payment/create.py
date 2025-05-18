from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from mercadopago import SDK
from src.services.mp_api import MP_ACCESS_TOKEN
from src.models.PaymentModels import PaymentPreference

_mp_sdk = SDK(access_token=MP_ACCESS_TOKEN)

def create_payment_preference(pref: PaymentPreference) -> dict:
    preference_client = _mp_sdk.preference()    
    try:
        payload = jsonable_encoder(pref, by_alias=True, exclude_none=True)
        preference_response = preference_client.create(payload)
        return preference_response["response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar preferência de pagamento: {e}")
