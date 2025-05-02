from fastapi import HTTPException
from services.mongo import connect
from typing import List

async def get_all_budgets() -> List[dict]:
    collection, client = connect("budgets")
    try:
        budgets = list(collection.find())
        
        for budget in budgets:
            budget["_id"] = str(budget["_id"])

        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orçamentos: {e}")
    finally:
        client.close()

async def get_pending_budgets() -> List[dict]:
    collection, client = connect("budgets")
    try:
        budgets = list(collection.find({"status": "Pendente"}))

        for budget in budgets:
            budget["_id"] = str(budget["_id"])

        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orçamentos pendentes: {e}")
    finally:
        client.close()