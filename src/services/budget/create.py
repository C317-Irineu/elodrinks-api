from fastapi import HTTPException
from src.services.mongo import connect
from models.BudgetModels import BudgetIn

async def create_budget(budget: BudgetIn) -> str:
    collection, client = connect("budgets")
    try:
        budget_data = budget.dict(by_alias=True, exclude_unset=True)

        result = collection.insert_one(budget_data)

        return str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir orçamento: {e}")
    finally:
        client.close()

