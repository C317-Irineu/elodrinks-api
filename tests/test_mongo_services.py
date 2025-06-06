import os
import pytest
import importlib

mongo_mod = importlib.import_module("src.services.mongo.mongo")
connect = mongo_mod.connect


# -------------------------------
# Fake classes para simular MongoClient
# -------------------------------
class FakeCollection:
    """Simula uma coleção do MongoDB."""
    pass


class FakeDatabase:
    """
    Simula um Database do MongoDB.
    __getitem__(collection_name) retorna uma FakeCollection.
    """
    def __getitem__(self, collection_name):
        return FakeCollection()


class FakeClient:
    """
    Simula um MongoClient.
    __getitem__(db_name) retorna uma FakeDatabase ou lança se configured.
    """
    def __init__(self, should_raise=False):
        self.should_raise = should_raise

    def __getitem__(self, db_name):
        if self.should_raise:
            raise Exception("Erro simulado de conexão ao banco")
        return FakeDatabase()


# -------------------------
# Tests para connect()
# -------------------------
def test_connect_success(monkeypatch):
    fake_client = FakeClient()

    # Substitui o atributo 'client' no módulo mongo_mod
    monkeypatch.setattr(mongo_mod, "client", fake_client, raising=False)

    # Override do DATABASE no módulo para usar nosso valor teste
    monkeypatch.setattr(mongo_mod, "DATABASE", "qualquer_db", raising=False)

    # Chamando connect, deve retornar (FakeCollection, fake_client)
    fake_collection, returned_client = connect("minha_colecao")
    assert isinstance(fake_collection, FakeCollection)
    assert returned_client is fake_client


def test_connect_missing_environment_variable(monkeypatch):
    fake_client = FakeClient()

    monkeypatch.setattr(mongo_mod, "client", fake_client, raising=False)
    # Define DATABASE como string vazia
    monkeypatch.setattr(mongo_mod, "DATABASE", "", raising=False)

    # Mesmo com DATABASE vazio, connect tentará usar client[""] e não gerará TypeError
    fake_collection, returned_client = connect("outra_colecao")
    assert isinstance(fake_collection, FakeCollection)
    assert returned_client is fake_client


def test_connect_failure(monkeypatch):
    bad_client = FakeClient(should_raise=True)

    # Patch do client para simular falha ao acessar client[DATABASE]
    monkeypatch.setattr(mongo_mod, "client", bad_client, raising=False)
    monkeypatch.setattr(mongo_mod, "DATABASE", "db_inexistente", raising=False)

    with pytest.raises(Exception) as excinfo:
        connect("colecao_nao_importa")

    assert "Erro simulado de conexão ao banco" in str(excinfo.value)
