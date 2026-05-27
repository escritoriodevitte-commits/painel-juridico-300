"""Testa o caminho Claude do endpoint de IA com o SDK mockado (sem rede)."""
from backend.tests.conftest import auth_header, login, register


class _Block:
    type = "text"
    text = "PETIÇÃO GERADA PELA IA (mock)."


class _Message:
    content = [_Block()]


class _Messages:
    def create(self, **kwargs):
        return _Message()


class _FakeAnthropic:
    def __init__(self, *a, **k):
        self.messages = _Messages()


def test_ia_peticao_claude(client, monkeypatch):
    import anthropic

    from backend.config import settings

    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setattr(anthropic, "Anthropic", _FakeAnthropic)

    register(client)
    token = login(client, "admin@a.com", "senha12345")
    r = client.post(
        "/api/v1/ia/peticao",
        json={
            "tipo": "reclamatória trabalhista",
            "cliente_nome": "João",
            "fatos": "Trabalhou sem registro.",
            "pedidos": "Vínculo e verbas.",
        },
        headers=auth_header(token),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["fonte"] == "claude"
    assert "mock" in body["texto"]
