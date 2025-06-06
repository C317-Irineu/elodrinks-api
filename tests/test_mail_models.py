import pytest
from pydantic import ValidationError

from src.models.MailModels import EmailDetails, EmailIn


# --------------------------
# Tests para EmailDetails
# --------------------------
def test_email_details_valid():
    data = {
        "email": "cliente@example.com",
        "name": "Cliente Teste",
        "type": "fatura",
        "date": "2025-06-04",
        "value": "R$ 150,00",
        "payment_link": "https://meusite.com/pagar/123",
    }
    details = EmailDetails(**data)
    assert details.email == "cliente@example.com"
    assert details.name == "Cliente Teste"
    assert details.type == "fatura"
    assert details.date == "2025-06-04"
    assert details.value == "R$ 150,00"
    assert details.payment_link == "https://meusite.com/pagar/123"


def test_email_details_missing_required_field():
    # Faltando "email"
    with pytest.raises(ValidationError) as excinfo1:
        EmailDetails(
            name="Sem Email",
            type="alerta",
            date="2025-07-01",
            value="R$ 50,00",
            payment_link="https://meusite.com/pagar/abc",
        )
    errors1 = excinfo1.value.errors()
    assert any(e["loc"] == ("email",) for e in errors1)

    # Faltando "payment_link"
    with pytest.raises(ValidationError) as excinfo2:
        EmailDetails(
            email="usuario@example.com",
            name="Sem Link",
            type="alerta",
            date="2025-07-01",
            value="R$ 50,00",
        )
    errors2 = excinfo2.value.errors()
    assert any(e["loc"] == ("payment_link",) for e in errors2)


def test_email_details_invalid_type_fields():
    # "name" deve ser str; passar int deve falhar
    with pytest.raises(ValidationError) as excinfo1:
        EmailDetails(
            email="cliente@example.com",
            name=123,  # inválido
            type="fatura",
            date="2025-06-04",
            value="R$ 150,00",
            payment_link="https://meusite.com/pagar/123",
        )
    errors1 = excinfo1.value.errors()
    assert any(e["loc"] == ("name",) for e in errors1)

    # "value" deve ser str; passar float deve falhar
    with pytest.raises(ValidationError) as excinfo2:
        EmailDetails(
            email="cliente@example.com",
            name="Teste",
            type="fatura",
            date="2025-06-04",
            value=150.0,  # inválido
            payment_link="https://meusite.com/pagar/123",
        )
    errors2 = excinfo2.value.errors()
    assert any(e["loc"] == ("value",) for e in errors2)


# --------------------------
# Tests para EmailIn
# --------------------------
def test_email_in_valid():
    data = {"_id": "email_001"}
    email_in = EmailIn(**data)
    assert email_in.id == "email_001"


def test_email_in_invalid_alias_usage():
    # Passar "id" em vez de "_id" deve falhar (faltando "_id")
    with pytest.raises(ValidationError) as excinfo:
        EmailIn(id="wrongalias")
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("_id",) for e in errors)
