from fastapi import HTTPException
from src.services.mongo import connect
from src.models.BudgetModels import BudgetIn, BudgetUpdate
from bson import ObjectId

async def create_budget(budget: BudgetIn) -> str:
    collection, client = connect("budgets")
    try:
        budget_data = budget.dict(by_alias=True, exclude_unset=True)

        result = collection.insert_one(budget_data)

        return str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir orçamento: {e}")

async def update_budget_status_and_value(budget_update: BudgetUpdate) -> None:
    collection, client = connect("budgets")
    try:
        update_fields = {"status": budget_update.new_status}
        if budget_update.value is not None:
            update_fields["value"] = budget_update.value

        result = collection.update_one(
            {"_id": ObjectId(budget_update.id)},
            {"$set": update_fields}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar orçamento: {e}")
