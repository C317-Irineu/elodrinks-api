import pytest
from bson import ObjectId
from fastapi import HTTPException

from src.models.BudgetModels import BudgetIn, BudgetUpdate
from src.services.budget.create import create_budget, update_budget_status_and_value
from src.services.budget.read import get_all_budgets, get_pending_budgets, get_budget_by_id


# -------------------------
# Fixtures and fakes
# -------------------------
class FakeInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeUpdateResult:
    def __init__(self, matched_count):
        self.matched_count = matched_count


class FakeCollection:
    def __init__(self):
        # Armazena documentos em um dicionário: chave é string do ObjectId
        self._docs = {}

    def insert_one(self, data):
        """
        Simula insert_one: gera um ObjectId, insere em _docs e retorna FakeInsertResult.
        """
        new_id = ObjectId()
        data["_id"] = new_id
        self._docs[str(new_id)] = data.copy()
        return FakeInsertResult(new_id)

    def update_one(self, filter_query, update_query):
        """
        Simula update_one: se encontrar, aplica "$set" e retorna matched_count=1;
        se não, matched_count=0.
        """
        oid = filter_query.get("_id")
        str_oid = str(oid)
        if str_oid in self._docs:
            set_fields = update_query.get("$set", {})
            self._docs[str_oid].update(set_fields)
            return FakeUpdateResult(matched_count=1)
        else:
            return FakeUpdateResult(matched_count=0)

    def find(self, filter_query=None):
        """
        Simula find: retorna lista de cópias de documentos. 
        Se filter_query tiver {"status": "Pendente"}, filtra apenas esses.
        """
        docs = list(self._docs.values())
        if filter_query and "status" in filter_query:
            status_val = filter_query["status"]
            docs = [d for d in docs if d.get("status") == status_val]
        return [d.copy() for d in docs]

    def find_one(self, filter_query):
        """
        Simula find_one: procura pelo "_id" em _docs e retorna cópia ou None.
        """
        oid = filter_query.get("_id")
        str_oid = str(oid)
        doc = self._docs.get(str_oid)
        return doc.copy() if doc else None


class FakeClient:
    """Fake client apenas para corresponder à assinatura connect()."""
    pass


@pytest.fixture
def fake_collection_and_client():
    """
    Fixture que retorna uma instância nova de FakeCollection e FakeClient.
    Usada para monkeypatch de connect().
    """
    return FakeCollection(), FakeClient()


# -------------------------
# Tests para create_budget
# -------------------------
@pytest.mark.asyncio
async def test_create_budget_success(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    # Monkeypatch para que connect("budgets") em src.services.budget.create use nosso fake
    def fake_connect(name):
        assert name == "budgets"
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.create.connect", fake_connect)

    # Cria um BudgetIn com dados mínimos válidos
    budget_payload = {
        "name": "Teste Cliente",
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
    budget_in = BudgetIn(**budget_payload)

    inserted_id_str = await create_budget(budget_in)
    # Após chamada, fake_coll._docs deve conter o documento inserido
    assert isinstance(inserted_id_str, str)
    assert inserted_id_str in fake_coll._docs
    stored = fake_coll._docs[inserted_id_str]
    # Verifica que o documento contém o alias "_id" e demais campos
    assert stored["_id"] == ObjectId(inserted_id_str)
    assert stored["name"] == "Teste Cliente"
    # Como excluímos unset, o campo "status" não estará presente por padrão
    assert "status" not in stored


@pytest.mark.asyncio
async def test_create_budget_insertion_error(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    # Faz insert_one lançar exceção
    class BadCollection(FakeCollection):
        def insert_one(self, data):
            raise Exception("Falha no banco")

    bad_coll = BadCollection()

    def fake_connect(name):
        return bad_coll, fake_client

    monkeypatch.setattr("src.services.budget.create.connect", fake_connect)

    budget_in = BudgetIn(
        name="Cliente Erro",
        email="erro@example.com",
        phone="(21) 98888-1111",
        budget={
            "description": "Evento Erro",
            "type": "Erro",
            "date": "2025-12-05",
            "num_barmans": 2,
            "num_guests": 20,
            "time": 3.0,
            "package": "Premium",
        },
    )
    with pytest.raises(HTTPException) as excinfo:
        await create_budget(budget_in)
    assert excinfo.value.status_code == 500
    assert "Falha no banco" in excinfo.value.detail


# ----------------------------------------------
# Tests para update_budget_status_and_value
# ----------------------------------------------
@pytest.mark.asyncio
async def test_update_budget_success(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client
    # Prepara um documento existente no fake_coll
    existing_id = ObjectId()
    fake_coll._docs[str(existing_id)] = {
        "_id": existing_id,
        "name": "Teste Existente",
        "email": "existente@example.com",
        "phone": "(31) 97777-2222",
        "budget": {
            "description": "Existente",
            "type": "Teste",
            "date": "2025-12-10",
            "num_barmans": 1,
            "num_guests": 5,
            "time": 1.0,
            "package": "Simples",
        },
        "status": "Pendente",
    }

    def fake_connect(name):
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.create.connect", fake_connect)

    # Cria BudgetUpdate para atualizar status e valor
    budget_update = BudgetUpdate(
        _id=str(existing_id),
        new_status="Aprovado",
        value=200.0,
    )
    # A chamada deve completar sem exceção
    await update_budget_status_and_value(budget_update)

    # Verifica que fake_coll._docs foi atualizado
    updated = fake_coll._docs[str(existing_id)]
    assert updated["status"] == "Aprovado"
    assert updated["value"] == 200.0


@pytest.mark.asyncio
async def test_update_budget_not_found(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    def fake_connect(name):
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.create.connect", fake_connect)

    nonexistent_id = str(ObjectId())
    budget_update = BudgetUpdate(_id=nonexistent_id, new_status="Rejeitado")

    with pytest.raises(HTTPException) as excinfo:
        await update_budget_status_and_value(budget_update)
    # O 404 interno é encapsulado no except e relançado como 500
    assert excinfo.value.status_code == 500
    assert "Orçamento não encontrado" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_budget_error(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    # Faz update_one lançar exceção
    class BadCollection(FakeCollection):
        def update_one(self, filter_query, update_query):
            raise Exception("Erro ao atualizar")

    bad_coll = BadCollection()

    def fake_connect(name):
        return bad_coll, fake_client

    monkeypatch.setattr("src.services.budget.create.connect", fake_connect)

    budget_update = BudgetUpdate(_id=str(ObjectId()), new_status="ErroTest")
    with pytest.raises(HTTPException) as excinfo:
        await update_budget_status_and_value(budget_update)
    assert excinfo.value.status_code == 500
    assert "Erro ao atualizar" in excinfo.value.detail


# -------------------------------
# Tests para get_all_budgets
# -------------------------------
@pytest.mark.asyncio
async def test_get_all_budgets_success(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    # Prepara dois documentos no fake_coll
    oid1 = ObjectId()
    oid2 = ObjectId()
    fake_coll._docs[str(oid1)] = {"_id": oid1, "status": "Pendente"}
    fake_coll._docs[str(oid2)] = {"_id": oid2, "status": "Confirmado"}

    def fake_connect(name):
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    results = await get_all_budgets()
    # Deve retornar lista de dicionários com "_id" convertido para string
    assert isinstance(results, list)
    ids = {item["_id"] for item in results}
    assert str(oid1) in ids and str(oid2) in ids
    # Cada item deve conter campo "status"
    for item in results:
        assert "status" in item


@pytest.mark.asyncio
async def test_get_all_budgets_error(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    class BadCollection(FakeCollection):
        def find(self, filter_query=None):
            raise Exception("Erro find")

    bad_coll = BadCollection()

    def fake_connect(name):
        return bad_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    with pytest.raises(HTTPException) as excinfo:
        await get_all_budgets()
    assert excinfo.value.status_code == 500
    assert "Erro find" in excinfo.value.detail


# ---------------------------------------------
# Tests para get_pending_budgets
# ---------------------------------------------
@pytest.mark.asyncio
async def test_get_pending_budgets_success(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    # Prepara três documentos, dois pendentes e um confirmado
    oid1 = ObjectId()
    oid2 = ObjectId()
    oid3 = ObjectId()
    fake_coll._docs[str(oid1)] = {"_id": oid1, "status": "Pendente"}
    fake_coll._docs[str(oid2)] = {"_id": oid2, "status": "Confirmado"}
    fake_coll._docs[str(oid3)] = {"_id": oid3, "status": "Pendente"}

    def fake_connect(name):
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    pendentes = await get_pending_budgets()
    assert isinstance(pendentes, list)
    # Apenas os com status "Pendente" devem aparecer
    ids = {item["_id"] for item in pendentes}
    assert str(oid1) in ids and str(oid3) in ids
    assert all(item.get("status") == "Pendente" for item in pendentes)


@pytest.mark.asyncio
async def test_get_pending_budgets_error(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    class BadCollection(FakeCollection):
        def find(self, filter_query=None):
            raise Exception("Erro pending")

    bad_coll = BadCollection()

    def fake_connect(name):
        return bad_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    with pytest.raises(HTTPException) as excinfo:
        await get_pending_budgets()
    assert excinfo.value.status_code == 500
    assert "Erro pending" in excinfo.value.detail


# -------------------------------------
# Tests para get_budget_by_id
# -------------------------------------
@pytest.mark.asyncio
async def test_get_budget_by_id_success(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    oid = ObjectId()
    fake_coll._docs[str(oid)] = {
        "_id": oid,
        "status": "Pendente",
        "name": "Cliente X",
    }

    def fake_connect(name):
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    result = await get_budget_by_id(str(oid))
    assert isinstance(result, dict)
    assert result["_id"] == str(oid)
    assert result["status"] == "Pendente"
    assert result["name"] == "Cliente X"


@pytest.mark.asyncio
async def test_get_budget_by_id_not_found(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    def fake_connect(name):
        return fake_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    with pytest.raises(HTTPException) as excinfo:
        await get_budget_by_id(str(ObjectId()))
    # O 404 interno é capturado e relançado como 500
    assert excinfo.value.status_code == 500
    assert "Orçamento não encontrado" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_budget_by_id_error(monkeypatch, fake_collection_and_client):
    fake_coll, fake_client = fake_collection_and_client

    class BadCollection(FakeCollection):
        def find_one(self, filter_query):
            raise Exception("Erro find_one")

    bad_coll = BadCollection()

    def fake_connect(name):
        return bad_coll, fake_client

    monkeypatch.setattr("src.services.budget.read.connect", fake_connect)

    with pytest.raises(HTTPException) as excinfo:
        await get_budget_by_id(str(ObjectId()))
    assert excinfo.value.status_code == 500
    assert "Erro find_one" in excinfo.value.detail
