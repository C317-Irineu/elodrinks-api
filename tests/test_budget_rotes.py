# tests/test_budget_routes.py

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import importlib

# Importa o módulo onde o router está definido
budget_routes_mod = importlib.import_module("src.routes.budget")
router = budget_routes_mod.router

from src.models.BudgetModels import BudgetIn, BudgetUpdate
from src.models.MailModels import EmailIn, EmailDetails


# -------------------------
# Fixture para criar FastAPI + TestClient
# -------------------------
@pytest.fixture
def app_client(monkeypatch):
    """
    Monkeypatch de connect em ambos os serviços de budget (create e read)
    para evitar chamadas reais ao MongoDB.
    """
    # connect em create retorna um par dummy (coleção vazia, cliente dummy)
    monkeypatch.setattr(
        "src.services.budget.create.connect",
        lambda name: (None, None),
        raising=False,
    )
    # connect em read retorna par dummy
    monkeypatch.setattr(
        "src.services.budget.read.connect",
        lambda name: (None, None),
        raising=False,
    )

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# -------------------------
# Testes para create_budget_route
# -------------------------
def test_create_budget_route_success(monkeypatch, app_client):
    async def fake_create_budget(budget: BudgetIn):
        return "fake_id_123"

    # Patch na referência dentro do módulo de rotas
    monkeypatch.setattr(
        "src.routes.budget.create_budget",
        fake_create_budget,
    )

    payload = {
        "name": "Cliente Teste",
        "email": "cliente@example.com",
        "phone": "(11) 99999-0000",
        "budget": {
            "description": "Evento Teste",
            "type": "Teste",
            "date": "2025-12-01",
            "num_barmans": 1,
            "num_guests": 10,
            "time": 2.0,
            "package": "Básico",
        },
    }

    response = app_client.post("/budget", json=payload)
    assert response.status_code == 201
    assert response.json() == {"id": "fake_id_123"}


def test_create_budget_route_internal_error(monkeypatch, app_client):
    async def fake_create_budget(budget: BudgetIn):
        raise Exception("Erro interno")

    monkeypatch.setattr(
        "src.routes.budget.create_budget",
        fake_create_budget,
    )

    payload = {
        "name": "Cliente Teste",
        "email": "cliente@example.com",
        "phone": "(11) 99999-0000",
        "budget": {
            "description": "Evento Teste",
            "type": "Teste",
            "date": "2025-12-01",
            "num_barmans": 1,
            "num_guests": 10,
            "time": 2.0,
            "package": "Básico",
        },
    }

    response = app_client.post("/budget", json=payload)
    assert response.status_code == 500
    assert "Erro interno" in response.json()["detail"]


# -------------------------
# Testes para update_budget_status_route
# -------------------------
def test_update_budget_status_route_success(monkeypatch, app_client):
    async def fake_update_budget(update_data: BudgetUpdate):
        return None  # sem erro

    monkeypatch.setattr(
        "src.routes.budget.update_budget_status_and_value",
        fake_update_budget,
    )

    payload = {"_id": "some_id", "new_status": "Aprovado", "value": 100.0}

    response = app_client.patch("/budget/status", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Status atualizado com sucesso"}


def test_update_budget_status_route_not_found(monkeypatch, app_client):
    async def fake_update_budget(update_data: BudgetUpdate):
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    monkeypatch.setattr(
        "src.routes.budget.update_budget_status_and_value",
        fake_update_budget,
    )

    payload = {"_id": "nonexistent", "new_status": "Rejeitado"}

    response = app_client.patch("/budget/status", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Orçamento não encontrado"


def test_update_budget_status_route_internal_error(monkeypatch, app_client):
    async def fake_update_budget(update_data: BudgetUpdate):
        raise Exception("Erro qualquer")

    monkeypatch.setattr(
        "src.routes.budget.update_budget_status_and_value",
        fake_update_budget,
    )

    payload = {"_id": "any_id", "new_status": "Rejeitado"}

    response = app_client.patch("/budget/status", json=payload)
    assert response.status_code == 500
    assert "Erro qualquer" in response.json()["detail"]


# -------------------------
# Testes para get_budgets_route (get_all_budgets)
# -------------------------
def test_get_budgets_route_success(monkeypatch, app_client):
    async def fake_get_all():
        return [{"_id": "id1", "status": "Pendente"}]

    monkeypatch.setattr(
        "src.routes.budget.get_all_budgets",
        fake_get_all,
    )

    response = app_client.get("/budget")
    assert response.status_code == 200
    assert response.json() == {"budgets": [{"_id": "id1", "status": "Pendente"}]}


def test_get_budgets_route_error(monkeypatch, app_client):
    async def fake_get_all():
        raise Exception("Falha ao buscar")

    monkeypatch.setattr(
        "src.routes.budget.get_all_budgets",
        fake_get_all,
    )

    response = app_client.get("/budget")
    assert response.status_code == 500
    assert "Falha ao buscar" in response.json()["detail"]


# -------------------------
# Testes para get_pending_budgets_route
# -------------------------
def test_get_pending_budgets_route_success(monkeypatch, app_client):
    async def fake_get_pending():
        return [{"_id": "id2", "status": "Pendente"}]

    monkeypatch.setattr(
        "src.routes.budget.get_pending_budgets",
        fake_get_pending,
    )

    response = app_client.get("/budget/pending")
    assert response.status_code == 200
    assert response.json() == {"budgets": [{"_id": "id2", "status": "Pendente"}]}


def test_get_pending_budgets_route_error(monkeypatch, app_client):
    async def fake_get_pending():
        raise Exception("Erro pendentes")

    monkeypatch.setattr(
        "src.routes.budget.get_pending_budgets",
        fake_get_pending,
    )

    response = app_client.get("/budget/pending")
    assert response.status_code == 500
    assert "Erro pendentes" in response.json()["detail"]


# -------------------------
# Testes para get_budget_by_id_route
# -------------------------
def test_get_budget_by_id_route_success(monkeypatch, app_client):
    async def fake_get_by_id(budget_id: str):
        return {"_id": budget_id, "status": "Confirmado"}

    monkeypatch.setattr(
        "src.routes.budget.get_budget_by_id",
        fake_get_by_id,
    )

    response = app_client.get("/budget/some_id")
    assert response.status_code == 200
    assert response.json() == {"budget": {"_id": "some_id", "status": "Confirmado"}}


def test_get_budget_by_id_route_not_found(monkeypatch, app_client):
    async def fake_get_by_id(budget_id: str):
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    monkeypatch.setattr(
        "src.routes.budget.get_budget_by_id",
        fake_get_by_id,
    )

    response = app_client.get("/budget/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Orçamento não encontrado"


def test_get_budget_by_id_route_error(monkeypatch, app_client):
    async def fake_get_by_id(budget_id: str):
        raise Exception("Erro ao buscar")

    monkeypatch.setattr(
        "src.routes.budget.get_budget_by_id",
        fake_get_by_id,
    )

    response = app_client.get("/budget/any")
    assert response.status_code == 500
    assert "Erro ao buscar" in response.json()["detail"]


# -------------------------
# Testes para send_budget_email_route
# -------------------------
def test_send_budget_email_route_success(monkeypatch, app_client):
    fake_budget = {
        "_id": "id_email",
        "name": "Cliente Email",
        "email": "cliente@mail.com",
        "budget": {"type": "Aniversário", "date": "2025-08-01"},
        "value": 250.0,
    }

    async def fake_get_by_id(budget_id: str):
        return fake_budget

    monkeypatch.setattr(
        "src.routes.budget.get_budget_by_id",
        fake_get_by_id,
    )

    def fake_create_preference(data: dict):
        return {"initPoint": "https://fake.init", "preferenceId": "pref123"}

    monkeypatch.setattr(
        "src.routes.budget.create_preference",
        fake_create_preference,
    )

    def fake_send_email(email_details: EmailDetails):
        assert email_details.email == fake_budget["email"]
        assert email_details.name == fake_budget["name"]
        assert email_details.payment_link == "https://fake.init"

    monkeypatch.setattr(
        "src.routes.budget.send_email",
        fake_send_email,
    )

    payload = {"_id": "id_email"}
    response = app_client.post("/budget/email/send", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Email enviado com sucesso"}


def test_send_budget_email_route_not_found(monkeypatch, app_client):
    async def fake_get_by_id(budget_id: str):
        return None

    monkeypatch.setattr(
        "src.routes.budget.get_budget_by_id",
        fake_get_by_id,
    )

    payload = {"_id": "nonexistent"}
    response = app_client.post("/budget/email/send", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Orçamento não encontrado"


def test_send_budget_email_route_internal_error(monkeypatch, app_client):
    async def fake_get_by_id(budget_id: str):
        raise Exception("Erro interno email")

    monkeypatch.setattr(
        "src.routes.budget.get_budget_by_id",
        fake_get_by_id,
    )

    payload = {"_id": "any"}
    response = app_client.post("/budget/email/send", json=payload)
    assert response.status_code == 500
    assert "Erro interno email" in response.json()["detail"]


# -------------------------
# Testes para webhook
# -------------------------
def test_webhook_not_payment(app_client):
    response = app_client.post("/budget/webhook", json={"type": "nonpayment"})
    assert response.status_code == 200
    assert response.json() == {"message": "Tipo de notificação não tratada"}


def test_webhook_payment_success(monkeypatch, app_client):
    fake_payment_info = {"response": {"status": "approved", "external_reference": "ext123"}}

    class FakePayment:
        def get(self, payment_id):
            return fake_payment_info

    class FakeSDK:
        def payment(self):
            return FakePayment()

    monkeypatch.setattr(budget_routes_mod, "sdk", FakeSDK())

    async def fake_update_budget(update_data: BudgetUpdate):
        assert update_data.id == "ext123"
        return None

    monkeypatch.setattr(
        "src.routes.budget.update_budget_status_and_value",
        fake_update_budget,
    )

    payload = {"type": "payment", "data": {"id": "pay123"}}
    response = app_client.post("/budget/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Notificação processada com sucesso"}


def test_webhook_payment_failure(monkeypatch, app_client):
    class FakePaymentError:
        def get(self, payment_id):
            raise Exception("Erro Mercado Pago")

    class FakeSDK:
        def payment(self):
            return FakePaymentError()

    monkeypatch.setattr(budget_routes_mod, "sdk", FakeSDK())

    payload = {"type": "payment", "data": {"id": "pay123"}}
    response = app_client.post("/budget/webhook", json=payload)
    assert response.status_code == 400
    assert "Erro ao processar pagamento" in response.json()["detail"]
