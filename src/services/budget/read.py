from fastapi import HTTPException
from src.services.mongo import connect
from typing import List
from bson import ObjectId

async def get_all_budgets() -> List[dict]:
    collection, client = connect("budgets")
    try:
        budgets = list(collection.find())
        
        for budget in budgets:
            budget["_id"] = str(budget["_id"])

        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orçamentos: {e}")

async def get_pending_budgets() -> List[dict]:
    collection, client = connect("budgets")
    try:
        budgets = list(collection.find({"status": "Pendente"}))

        for budget in budgets:
            budget["_id"] = str(budget["_id"])

        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orçamentos pendentes: {e}")
    
async def get_budget_by_id(budget_id: str) -> dict:
    collection, client = connect("budgets")
    try:
        budget = collection.find_one({"_id": ObjectId(budget_id)})
        if not budget:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")
        budget["_id"] = str(budget["_id"])
        return budget
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orçamento: {e}")
