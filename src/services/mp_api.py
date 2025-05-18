import os
from dotenv import load_dotenv

load_dotenv()

MP_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
MP_PUBLIC_KEY   = os.getenv("MERCADOPAGO_PUBLIC_KEY")

if not MP_ACCESS_TOKEN or not MP_PUBLIC_KEY:
    raise RuntimeError("Credenciais do Mercado Pago não encontradas. Verifique o .env")
