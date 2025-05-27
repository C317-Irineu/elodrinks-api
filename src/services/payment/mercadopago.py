import mercadopago
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))

BACK_URLS = {
    "success": "https://clara-portfolio-olive.vercel.app/",
    "failure": "https://clara-portfolio-olive.vercel.app/",
    "pending": "https://clara-portfolio-olive.vercel.app/",
}

def create_preference(data: dict):
    preference_data = {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "title": data["title"],
                "description": data.get("description", ""),
                "unit_price": data["unit_price"],
                "quantity": data["quantity"],
            }
        ],
        "payer": {
            "email": data["email"],
        },
        "back_urls": BACK_URLS,
        "auto_return": data.get("auto_return", "approved"),
        "external_reference": data["id"],
        "payment_methods": {
            "excluded_payment_types": [],
            "installments": 12,
            "default_payment_method_id": None,
            "included_payment_methods": [
                { "id": "pix" },
                { "id": "credit_card" }
            ]
        }
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        init_point = preference_response["response"]["init_point"]
        preference_id = preference_response["response"]["id"]

        return {
            "initPoint": init_point,
            "preferenceId": preference_id
        }

    except Exception as e:
        raise Exception(f"Erro ao criar preferência de pagamento: {str(e)}")
