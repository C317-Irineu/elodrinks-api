from fastapi import APIRouter, HTTPException, Request
import mercadopago
from src.models.BudgetModels import BudgetIn, BudgetUpdate
from src.models.MailModels import EmailIn, EmailDetails
from src.services.budget.create import create_budget, update_budget_status_and_value
from src.services.budget.read import get_all_budgets, get_pending_budgets, get_budget_by_id
from src.services.payment import create_preference
from src.services.email import send_email
from dotenv import load_dotenv
import os

load_dotenv()

sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))

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
            
        preference = {
            "title": f"Orçamento EloDrinks - {budget['name']}",
            "description": f"Orçamento para {budget['budget']['type']} na data {budget['budget']['date']}",
            "unit_price": budget["value"],
            "quantity": 1,
            "email": budget["email"],
            "id": str(budget["_id"]),
            "auto_return": "approved"
        }
        
        #TODO: Implementar logica de pegar o external reference como id do orçamento
        link = create_preference(preference).get("initPoint")
        
        email_details = EmailDetails(
            email=budget["email"],
            name=budget["name"],
            type=budget["budget"]["type"],
            date=budget["budget"]["date"],
            value=str(budget["value"]),
            payment_link=link
        )
                
        send_email(email_details)
        
        return {"message": "Email enviado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    
    if "type" in body and body["type"] == "payment":
        payment_id = body["data"]["id"]

        try:
            payment_info = sdk.payment().get(payment_id)
            status = payment_info["response"]["status"]
            external_reference = payment_info["response"]["external_reference"]

            print(f"Pagamento recebido: ID={payment_id}, status={status}, ref={external_reference}")

            #TODO: Implementar logica de pegar o external reference como id do orçamento
            update_data = BudgetUpdate(
                _id=external_reference,
                new_status="paid" if status == "approved" else "failed"
            )
            
            await update_budget_status_and_value(update_data)
            
            return {"message": "Notificação processada com sucesso"}
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao processar pagamento: {str(e)}")
    
    return {"message": "Tipo de notificação não tratada"}
