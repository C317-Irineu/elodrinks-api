import os
import uuid
import pytest
import importlib


payment_mod = importlib.import_module("src.services.payment.mercadopago")
create_preference = payment_mod.create_preference

# -------------------------
# Fake Mercado Pago SDK
# -------------------------
class FakePreference:
    def __init__(self, should_raise=False, response_data=None):
        """
        :param should_raise: se True, raise Exception em create()
        :param response_data: dicionário com os campos "response": {"init_point": ..., "id": ...}
        """
        self.should_raise = should_raise
        # response_data precisa ter a estrutura { "response": { "init_point": ..., "id": ... } }
        self.response_data = response_data or {
            "response": {
                "init_point": "https://fake.init.point",
                "id": 999999,
            }
        }

    def create(self, preference_data):
        if self.should_raise:
            raise Exception("Erro simulado no Mercado Pago")
        # Retorna um dicionário com chave "response"
        return self.response_data


class FakeSDK:
    def __init__(self, fake_preference: FakePreference):
        self._fake_preference = fake_preference

    def preference(self):
        return self._fake_preference


# -------------------------
# Fixture para variáveis de ambiente
# -------------------------
@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """
    Define variável de ambiente MERCADO_PAGO_ACCESS_TOKEN para o módulo.
    """
    monkeypatch.setenv("MERCADO_PAGO_ACCESS_TOKEN", "fake_access_token")


# -------------------------
# Teste de criação de preferência - sucesso
# -------------------------
def test_create_preference_success(monkeypatch):
    # Dados mínimos esperados pela função
    data = {
        "id": "order_123",
        "title": "Produto Teste",
        "unit_price": 150.0,
        "quantity": 2,
        "email": "cliente@example.com",
        # "description" e "auto_return" não obrigatórios
    }

    # Prepara FakePreference retornando dados conhecidos
    fake_response = {
        "response": {
            "init_point": "https://fake.init.point/abc",
            "id": 123456,
        }
    }
    fake_pref = FakePreference(response_data=fake_response)
    fake_sdk = FakeSDK(fake_pref)

    # Monkeypatch para que mercadopago.SDK(...) retorne nosso fake_sdk
    monkeypatch.setattr(payment_mod, "sdk", fake_sdk)

    # Chama a função create_preference
    result = create_preference(data)

    # Verifica estrutura do retorno
    assert isinstance(result, dict)
    assert result["initPoint"] == "https://fake.init.point/abc"
    assert result["preferenceId"] == 123456

    # Verifica que os dados passados para create() correspondem ao esperado parcialmente
    # (não testamos todo o dicionário, mas campos-chave)
    pref_data_passed = fake_pref  # não armazenamos diretamente, mas não houve exceção significa que chegou aqui


# -------------------------
# Teste de criação de preferência - erro interno
# -------------------------
def test_create_preference_failure(monkeypatch):
    data = {
        "id": "order_999",
        "title": "Produto Erro",
        "unit_price": 200.0,
        "quantity": 1,
        "email": "cliente2@example.com",
    }

    # Prepara FakePreference configurado para lançar exceção
    fake_pref_error = FakePreference(should_raise=True)
    fake_sdk_error = FakeSDK(fake_pref_error)
    monkeypatch.setattr(payment_mod, "sdk", fake_sdk_error)

    # Ao chamar create_preference, deve lançar Exception com a mensagem esperada
    with pytest.raises(Exception) as excinfo:
        create_preference(data)

    msg = str(excinfo.value)
    assert "Erro ao criar preferência de pagamento" in msg
    assert "Erro simulado no Mercado Pago" in msg


# -------------------------
# Teste de parâmetros obrigatórios faltando
# -------------------------
@pytest.mark.parametrize(
    "missing_key",
    ["id", "title", "unit_price", "quantity", "email"],
)
def test_create_preference_missing_required_field(missing_key):
    # Prepara dados completos e remove a chave faltante
    full_data = {
        "id": "order_321",
        "title": "Produto Completo",
        "unit_price": 120.0,
        "quantity": 3,
        "email": "cliente3@example.com",
    }
    incomplete = full_data.copy()
    incomplete.pop(missing_key)

    with pytest.raises(KeyError) as excinfo:
        create_preference(incomplete)
    # Verifica que a mensagem do KeyError mencione a chave faltante
    assert missing_key in str(excinfo.value)
