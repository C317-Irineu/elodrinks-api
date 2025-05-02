from typing import List
from fastapi import APIRouter, Depends, Security
# from dependencies import get_api_key, get_current_user

from src.models.BudgetModels import BudgetIn, Budget
from src.services.budget import create_budget, get_pending_budgets

router = APIRouter(
    prefix="/budgets",
    tags=["Budget"]
    # dependencies=[Depends(get_api_key)],
)


@router.post("/create", description="Create a new budget")
async def create_budget_endpoint(budget: BudgetIn):
    try:
        _id = await create_budget(budget)
        return {"message": f"Budget with id {_id} created successfully!"}
    except Exception as e:
        raise e


@router.get("/pending", description="Get all pending budgets", response_model=List[Budget])
async def get_pending_budgets_endpoint():
    try:
        budgets = await get_pending_budgets()
        return budgets
    except Exception as e:
        raise e
