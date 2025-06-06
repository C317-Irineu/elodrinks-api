import pytest
from pydantic import ValidationError

from src.models.PaymentModels import Item, BackUrls, PaymentPreference


# -----------------------
# Tests para Item model
# -----------------------
def test_item_valid_minimum_fields():
    data = {
        "_id": "item123",
        "title": "Produto X",
        "quantity": 2,
        "unit_price": 50.0,
    }
    item = Item(**data)
    assert item.id == "item123"         # alias _id → id
    assert item.title == "Produto X"
    assert item.quantity == 2
    assert item.unit_price == 50.0
    # Campos opcionais não informados devem ser None
    assert item.description is None
    assert item.currency_id is None


def test_item_all_fields_present():
    data = {
        "_id": "item456",
        "title": "Produto Y",
        "description": "Descrição detalhada",
        "quantity": 5,
        "currency_id": "BRL",
        "unit_price": 120.0,
    }
    item = Item(**data)
    assert item.id == "item456"
    assert item.title == "Produto Y"
    assert item.description == "Descrição detalhada"
    assert item.quantity == 5
    assert item.currency_id == "BRL"
    assert item.unit_price == 120.0


def test_item_missing_required_fields():
    # Faltando "_id"
    with pytest.raises(ValidationError) as excinfo1:
        Item(
            title="Produto Sem ID",
            quantity=1,
            unit_price=10.0,
        )
    errors1 = excinfo1.value.errors()
    assert any(e["loc"] == ("_id",) for e in errors1)

    # Faltando "title"
    with pytest.raises(ValidationError) as excinfo2:
        Item(
            _id="no_title",
            quantity=1,
            unit_price=10.0,
        )
    errors2 = excinfo2.value.errors()
    assert any(e["loc"] == ("title",) for e in errors2)

    # Faltando "quantity"
    with pytest.raises(ValidationError) as excinfo3:
        Item(
            _id="no_quantity",
            title="Sem Quantidade",
            unit_price=10.0,
        )
    errors3 = excinfo3.value.errors()
    assert any(e["loc"] == ("quantity",) for e in errors3)

    # Faltando "unit_price"
    with pytest.raises(ValidationError) as excinfo4:
        Item(
            _id="no_price",
            title="Sem Preço",
            quantity=3,
        )
    errors4 = excinfo4.value.errors()
    assert any(e["loc"] == ("unit_price",) for e in errors4)


def test_item_invalid_type_fields():
    # quantity deve ser int
    with pytest.raises(ValidationError) as excinfo1:
        Item(
            _id="bad_quantity",
            title="Teste",
            quantity="dois",   # inválido
            unit_price=5.0,
        )
    errors1 = excinfo1.value.errors()
    assert any(e["loc"] == ("quantity",) for e in errors1)

    # unit_price deve ser float
    with pytest.raises(ValidationError) as excinfo2:
        Item(
            _id="bad_price",
            title="Teste",
            quantity=1,
            unit_price="dez",   # inválido
        )
    errors2 = excinfo2.value.errors()
    assert any(e["loc"] == ("unit_price",) for e in errors2)

    # description deve ser str ou None; passar número deve falhar
    with pytest.raises(ValidationError) as excinfo3:
        Item(
            _id="bad_description",
            title="Teste",
            description=123,   # inválido
            quantity=1,
            unit_price=10.0,
        )
    errors3 = excinfo3.value.errors()
    assert any(e["loc"] == ("description",) for e in errors3)

    # currency_id deve ser str ou None; passar número deve falhar
    with pytest.raises(ValidationError) as excinfo4:
        Item(
            _id="bad_currency",
            title="Teste",
            quantity=1,
            currency_id=999,   # inválido
            unit_price=10.0,
        )
    errors4 = excinfo4.value.errors()
    assert any(e["loc"] == ("currency_id",) for e in errors4)


def test_item_invalid_alias_usage():
    # Passar "id" em vez de "_id" deve falhar (faltando "_id")
    with pytest.raises(ValidationError) as excinfo:
        Item(
            id="wrongalias",
            title="Teste",
            quantity=1,
            unit_price=10.0,
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("_id",) for e in errors)


# -------------------------
# Tests para BackUrls model
# -------------------------
def test_backurls_valid():
    data = {
        "success": "https://meusite.com/sucesso",
        "failure": "https://meusite.com/falha",
        "pending": "https://meusite.com/pendente",
    }
    urls = BackUrls(**data)
    assert urls.success == "https://meusite.com/sucesso"
    assert urls.failure == "https://meusite.com/falha"
    assert urls.pending == "https://meusite.com/pendente"


def test_backurls_missing_required_fields():
    # Faltando "failure"
    with pytest.raises(ValidationError) as excinfo1:
        BackUrls(
            success="https://meusite.com/sucesso",
            pending="https://meusite.com/pendente",
        )
    errors1 = excinfo1.value.errors()
    assert any(e["loc"] == ("failure",) for e in errors1)

    # Faltando "pending"
    with pytest.raises(ValidationError) as excinfo2:
        BackUrls(
            success="https://meusite.com/sucesso",
            failure="https://meusite.com/falha",
        )
    errors2 = excinfo2.value.errors()
    assert any(e["loc"] == ("pending",) for e in errors2)


def test_backurls_invalid_type_fields():
    # "success" deve ser str; passar int deve falhar
    with pytest.raises(ValidationError) as excinfo1:
        BackUrls(
            success=123,
            failure="https://meusite.com/falha",
            pending="https://meusite.com/pendente",
        )
    errors1 = excinfo1.value.errors()
    assert any(e["loc"] == ("success",) for e in errors1)

    # "failure" deve ser str; passar None deve falhar (None não é permitido)
    with pytest.raises(ValidationError) as excinfo2:
        BackUrls(
            success="https://meusite.com/sucesso",
            failure=None,
            pending="https://meusite.com/pendente",
        )
    errors2 = excinfo2.value.errors()
    assert any(e["loc"] == ("failure",) for e in errors2)


# ---------------------------------------
# Tests para PaymentPreference model
# ---------------------------------------
def test_payment_preference_valid_minimum():
    # Apenas o campo obrigatório "items"
    items_data = [
        {
            "_id": "itemA",
            "title": "Produto A",
            "quantity": 1,
            "unit_price": 100.0,
        }
    ]
    pref = PaymentPreference(items=items_data)
    assert isinstance(pref.items, list)
    assert pref.items[0].id == "itemA"
    # Campos opcionais não informados
    assert pref.payer is None
    assert pref.back_urls is None
    assert pref.external_reference is None
    assert pref.binary_mode is False  # default
    assert pref.auto_return is None


def test_payment_preference_all_fields():
    items_data = [
        {
            "_id": "itemX",
            "title": "Produto X",
            "description": "Desc X",
            "quantity": 3,
            "currency_id": "USD",
            "unit_price": 20.0,
        },
        {
            "_id": "itemY",
            "title": "Produto Y",
            "quantity": 2,
            "unit_price": 15.0,
        },
    ]
    payer_info = {"email": "cliente@example.com", "name": "Cliente Teste"}
    back_urls_data = {
        "success": "https://meusite.com/sucesso",
        "failure": "https://meusite.com/falha",
        "pending": "https://meusite.com/pendente",
    }
    pref = PaymentPreference(
        items=items_data,
        payer=payer_info,
        back_urls=back_urls_data,
        external_reference="ref123",
        binary_mode=True,
        auto_return="approved",
    )
    # Verifica lista de itens
    assert len(pref.items) == 2
    assert pref.items[0].description == "Desc X"
    assert pref.items[1].currency_id is None
    # Verifica dados do payer
    assert pref.payer == payer_info
    # Verifica parsing de BackUrls
    assert pref.back_urls.success == "https://meusite.com/sucesso"
    # Campos opcionais
    assert pref.external_reference == "ref123"
    assert pref.binary_mode is True
    assert pref.auto_return == "approved"


def test_payment_preference_missing_items():
    # "items" é obrigatório
    with pytest.raises(ValidationError) as excinfo:
        PaymentPreference()
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("items",) for e in errors)


def test_payment_preference_invalid_items_type():
    # items deve ser lista; passar dicionário único falha
    with pytest.raises(ValidationError) as excinfo:
        PaymentPreference(items={"_id": "item1", "title": "X", "quantity": 1, "unit_price": 10.0})
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("items",) for e in errors)


def test_payment_preference_invalid_nested_item():
    # Dentro de items, um dos itens está com tipo errado
    bad_items = [
        {
            "_id": "itemBad",
            "title": "Prod Bad",
            "quantity": "um",      # inválido
            "unit_price": 10.0,
        }
    ]
    with pytest.raises(ValidationError) as excinfo:
        PaymentPreference(items=bad_items)
    errors = excinfo.value.errors()
    # Localização: items → índice 0 → quantity
    assert any(
        e["loc"] == ("items", 0, "quantity") for e in errors
    )


def test_payment_preference_invalid_back_urls_type():
    items_data = [
        {"_id": "item1", "title": "Produto1", "quantity": 1, "unit_price": 5.0}
    ]
    # back_urls deve ser BackUrls ou dict com campos corretos; passar string falha
    with pytest.raises(ValidationError) as excinfo:
        PaymentPreference(
            items=items_data,
            back_urls="https://meusite.com"  # inválido
        )
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("back_urls",) for e in errors)
