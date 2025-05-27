from fastapi import APIRouter, HTTPException
from src.models.BudgetModels import BudgetIn, BudgetUpdate
from src.models.MailModels import EmailIn, EmailDetails
from src.services.budget.create import create_budget, update_budget_status_and_value
from src.services.budget.read import get_all_budgets, get_pending_budgets, get_budget_by_id
from src.services.email import send_email


router = APIRouter(prefix="/budget", tags=["budget"])

@router.post("", status_code=201, response_model=dict)
async def create_budget_route(budget: BudgetIn):
    try:
        inserted_id = await create_budget(budget)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/status", status_code=200, response_model=dict)
async def update_budget_status_route(update_data: BudgetUpdate):
    try:
        await update_budget_status_and_value(update_data)
        return {"message": "Status atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("", status_code=200, response_model=dict)
async def get_budgets_route():
    try:
        budgets = await get_all_budgets()
        return {"budgets": budgets}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/pending", status_code=200, response_model=dict)
async def get_pending_budgets_route():
    try:
        budgets = await get_pending_budgets()
        return {"budgets": budgets}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{budget_id}", status_code=200, response_model=dict)
async def get_budget_by_id_route(budget_id: str):
    try:
        budget = await get_budget_by_id(budget_id)
        return {"budget": budget}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/email/send", status_code=200, response_model=dict)
async def send_budget_email_route(emailIn: EmailIn):
    try:
        budget = await get_budget_by_id(emailIn.id)
        if not budget:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")
        
        email_details = EmailDetails(
            email=budget["email"],
            name=budget["name"],
            type=budget["budget"]["type"],
            date=budget["budget"]["date"],
            value=str(budget["value"]),
            payment_link="https://www.elodrinks.com/pagamento"  # Placeholder link
        )
        
        send_email(email_details)
        
        return {"message": "Email enviado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))