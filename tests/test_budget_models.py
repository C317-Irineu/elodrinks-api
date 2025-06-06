import pytest
from pydantic import ValidationError, EmailStr

from src.models.BudgetModels import (
    BudgetDetails,
    BudgetDetailsUpdate,
    BudgetIn,
    BudgetUpdate,
    Budget,
)


# -------------------------------
# Tests for BudgetDetails model
# -------------------------------
def test_budget_details_valid():
    details = BudgetDetails(
        description="Evento Corporativo",
        type="Corporativo",
        date="2025-07-15",
        num_barmans=3,
        num_guests=100,
        time=4.5,
        package="Premium",
        extras=["DJ", "Decoracao"],
    )
    assert details.description == "Evento Corporativo"
    assert details.type == "Corporativo"
    assert details.date == "2025-07-15"
    assert details.num_barmans == 3
    assert details.num_guests == 100
    assert details.time == 4.5
    assert details.package == "Premium"
    assert details.extras == ["DJ", "Decoracao"]


def test_budget_details_extras_optional():
    # When 'extras' is omitted, it should default to None
    details = BudgetDetails(
        description="Casamento",
        type="Social",
        date="2025-09-10",
        num_barmans=2,
        num_guests=50,
        time=3.0,
        package="Básico",
    )
    assert details.extras is None


def test_budget_details_missing_required_field():
    # Missing 'description' should raise ValidationError
    with pytest.raises(ValidationError) as excinfo:
        BudgetDetails(
            type="Social",
            date="2025-09-10",
            num_barmans=2,
            num_guests=50,
            time=3.0,
            package="Básico",
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("description",) for e in errors)


def test_budget_details_invalid_type_field():
    # 'num_barmans' must be int; passing string should raise
    with pytest.raises(ValidationError) as excinfo:
        BudgetDetails(
            description="Festa Infantil",
            type="Infantil",
            date="2025-08-01",
            num_barmans="dois",  # invalid
            num_guests=30,
            time=2.0,
            package="Kids",
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("num_barmans",) for e in errors)

    # 'extras' must be list of strings if provided
    with pytest.raises(ValidationError) as excinfo2:
        BudgetDetails(
            description="Aniversário",
            type="Social",
            date="2025-10-05",
            num_barmans=1,
            num_guests=20,
            time=2.5,
            package="Simples",
            extras=[123, 456],  # invalid, not strings
        )
    errors2 = excinfo2.value.errors()
    assert any("extras" in e["loc"] for e in errors2)


# --------------------------------------
# Tests for BudgetDetailsUpdate model
# --------------------------------------
def test_budget_details_update_empty():
    # All fields are optional; instantiating with no args should set all to None
    update = BudgetDetailsUpdate()
    assert update.description is None
    assert update.type is None
    assert update.date is None
    assert update.num_barmans is None
    assert update.num_guests is None
    assert update.time is None
    assert update.package is None
    assert update.extras is None


def test_budget_details_update_partial():
    update = BudgetDetailsUpdate(
        num_guests=80,
        package="Intermediário",
    )
    assert update.num_guests == 80
    assert update.package == "Intermediário"
    # Other optional fields remain None
    assert update.description is None
    assert update.extras is None


def test_budget_details_update_invalid_type():
    # num_guests should be int; passing string raises ValidationError
    with pytest.raises(ValidationError) as excinfo:
        BudgetDetailsUpdate(num_guests="oitenta")  # invalid
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("num_guests",) for e in errors)


# -----------------------------
# Tests for BudgetIn model
# -----------------------------
def test_budget_in_valid():
    details = {
        "description": "Evento Teste",
        "type": "Teste",
        "date": "2025-11-20",
        "num_barmans": 2,
        "num_guests": 60,
        "time": 5.0,
        "package": "TestePlus",
        "extras": ["Som", "Iluminação"],
    }
    budget_in = BudgetIn(
        name="João Silva",
        email="joao@example.com",
        phone="(11) 99999-0000",
        budget=details,
    )
    assert budget_in.name == "João Silva"
    assert budget_in.email == "joao@example.com"
    assert budget_in.phone == "(11) 99999-0000"
    # Nested BudgetDetails should be parsed correctly
    assert budget_in.budget.description == "Evento Teste"
    assert budget_in.status == "Pendente"  # default value
    assert budget_in.value is None  # default


def test_budget_in_invalid_email():
    details = {
        "description": "Evento Teste",
        "type": "Teste",
        "date": "2025-11-20",
        "num_barmans": 2,
        "num_guests": 60,
        "time": 5.0,
        "package": "TestePlus",
    }
    with pytest.raises(ValidationError) as excinfo:
        BudgetIn(
            name="Maria",
            email="maria-at-example.com",  # invalid email
            phone="(21) 98888-1111",
            budget=details,
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("email",) for e in errors)


def test_budget_in_missing_nested_required_field():
    # Nested BudgetDetails missing 'type'
    details_invalid = {
        "description": "Evento Sem Tipo",
        "date": "2025-12-01",
        "num_barmans": 1,
        "num_guests": 30,
        "time": 2.0,
        "package": "Básico",
    }
    with pytest.raises(ValidationError) as excinfo:
        BudgetIn(
            name="Pedro",
            email="pedro@example.com",
            phone="(31) 97777-2222",
            budget=details_invalid,
        )
    errors = excinfo.value.errors()
    # Ensure the error comes from missing 'type' in the nested model
    assert any(e["loc"][0] == "budget" and e["loc"][-1] == "type" for e in errors)


# -------------------------------
# Tests for BudgetUpdate model
# -------------------------------
def test_budget_update_valid():
    update = BudgetUpdate(
        _id="abcd1234",
        new_status="Aprovado",
    )
    assert update.id == "abcd1234"  # alias _id maps to .id
    assert update.new_status == "Aprovado"
    assert update.value is None  # default


def test_budget_update_missing_new_status():
    # 'new_status' is required
    with pytest.raises(ValidationError) as excinfo:
        BudgetUpdate(_id="xyz987")
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("new_status",) for e in errors)


def test_budget_update_invalid_alias_usage():
    # Passing 'id' instead of '_id' should raise
    with pytest.raises(ValidationError) as excinfo:
        BudgetUpdate(id="wrongfield", new_status="Rejeitado")
    errors = excinfo.value.errors()
    # Ensure the error indicates that 'id' is not a valid field
    assert any(e["loc"] == ("_id",) for e in errors)


# -------------------------
# Tests for Budget model
# -------------------------
def test_budget_valid():
    details = {
        "description": "Evento Completo",
        "type": "Completo",
        "date": "2025-07-30",
        "num_barmans": 4,
        "num_guests": 150,
        "time": 6.0,
        "package": "VIP",
    }
    budget = Budget(
        _id="unique123",
        name="Empresa XYZ",
        email="contato@empresa.xyz",
        phone="(41) 96666-3333",
        budget=details,
        status="Confirmado",
    )
    assert budget.id == "unique123"
    assert budget.name == "Empresa XYZ"
    assert budget.email == "contato@empresa.xyz"
    assert budget.phone == "(41) 96666-3333"
    assert budget.budget.num_guests == 150
    assert budget.status == "Confirmado"
    assert budget.value is None  # default


def test_budget_missing_required_field():
    # Missing 'name' should raise ValidationError
    with pytest.raises(ValidationError) as excinfo:
        Budget(
            _id="no_name",
            email="semnome@example.com",
            phone="(51) 95555-4444",
            budget={
                "description": "Sem Nome",
                "type": "Teste",
                "date": "2025-08-20",
                "num_barmans": 1,
                "num_guests": 10,
                "time": 1.5,
                "package": "Simples",
            },
            status="Pendente",
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


def test_budget_invalid_alias_usage():
    # Passing 'id' instead of '_id' should raise ValidationError
    with pytest.raises(ValidationError) as excinfo:
        Budget(
            id="badalias",
            name="Teste",
            email="teste@example.com",
            phone="(61) 94444-5555",
            budget={
                "description": "Alias Errado",
                "type": "Teste",
                "date": "2025-09-15",
                "num_barmans": 2,
                "num_guests": 40,
                "time": 3.0,
                "package": "Básico",
            },
            status="Pendente",
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("_id",) for e in errors)
