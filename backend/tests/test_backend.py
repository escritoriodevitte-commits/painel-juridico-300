from backend.tests.conftest import auth_header, login, register


def _admin_token(client, **kw):
    register(client, **kw)
    return login(client, kw.get("email", "admin@a.com"), kw.get("senha", "senha12345"))


def test_register_login_me(client):
    register(client)
    token = login(client, "admin@a.com", "senha12345")
    r = client.get("/api/v1/auth/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["role"] == "admin"


def test_login_senha_errada(client):
    register(client)
    r = client.post(
        "/api/v1/auth/login", data={"username": "admin@a.com", "password": "errada00"}
    )
    assert r.status_code == 401


def test_register_email_duplicado(client):
    register(client)
    r = client.post(
        "/api/v1/auth/register",
        json={
            "tenant_nome": "Outro",
            "nome": "X",
            "email": "admin@a.com",
            "senha": "senha12345",
        },
    )
    assert r.status_code == 409


def test_cliente_crud(client):
    token = _admin_token(client)
    h = auth_header(token)
    r = client.post("/api/v1/clientes", json={"nome": "Maria"}, headers=h)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.get("/api/v1/clientes", headers=h).json()[0]["nome"] == "Maria"
    r = client.put(
        f"/api/v1/clientes/{cid}", json={"nome": "Maria Silva"}, headers=h
    )
    assert r.json()["nome"] == "Maria Silva"
    assert client.delete(f"/api/v1/clientes/{cid}", headers=h).status_code == 204


def test_rbac_cliente_role_nao_cria(client):
    token = _admin_token(client)
    h = auth_header(token)
    client.post(
        "/api/v1/auth/users",
        json={
            "nome": "Cli",
            "email": "cli@a.com",
            "senha": "senha12345",
            "role": "cliente",
        },
        headers=h,
    )
    cli_token = login(client, "cli@a.com", "senha12345")
    r = client.post(
        "/api/v1/clientes", json={"nome": "X"}, headers=auth_header(cli_token)
    )
    assert r.status_code == 403
    # leitura é permitida
    assert client.get("/api/v1/clientes", headers=auth_header(cli_token)).status_code == 200


def test_tenant_isolation(client):
    ta = _admin_token(client, tenant="A", email="admin@a.com")
    cid = client.post(
        "/api/v1/clientes", json={"nome": "Cliente A"}, headers=auth_header(ta)
    ).json()["id"]

    tb = _admin_token(client, tenant="B", email="admin@b.com")
    # tenant B não vê clientes de A
    assert client.get("/api/v1/clientes", headers=auth_header(tb)).json() == []
    # e não acessa por id
    r = client.get(f"/api/v1/clientes/{cid}", headers=auth_header(tb))
    assert r.status_code == 404


def test_processo_andamento_audiencia(client):
    token = _admin_token(client)
    h = auth_header(token)
    cid = client.post("/api/v1/clientes", json={"nome": "C"}, headers=h).json()["id"]
    pid = client.post(
        "/api/v1/processos",
        json={"cliente_id": cid, "numero": "0001-22.2026.5.02.0001"},
        headers=h,
    ).json()["id"]
    assert (
        client.post(
            f"/api/v1/processos/{pid}/andamentos",
            json={"descricao": "Distribuído"},
            headers=h,
        ).status_code
        == 201
    )
    a = client.post(
        f"/api/v1/processos/{pid}/audiencias",
        json={"data": "2026-07-01T14:00:00", "tipo": "instrução", "local": "Vara 1"},
        headers=h,
    )
    assert a.status_code == 201
    assert len(client.get(f"/api/v1/processos/{pid}/audiencias", headers=h).json()) == 1


def test_financeiro_rbac(client):
    token = _admin_token(client)
    h = auth_header(token)
    cid = client.post("/api/v1/clientes", json={"nome": "C"}, headers=h).json()["id"]
    for email, role in [("adv@a.com", "advogado"), ("fin@a.com", "financeiro")]:
        client.post(
            "/api/v1/auth/users",
            json={"nome": role, "email": email, "senha": "senha12345", "role": role},
            headers=h,
        )
    adv = auth_header(login(client, "adv@a.com", "senha12345"))
    fin = auth_header(login(client, "fin@a.com", "senha12345"))

    payload = {"cliente_id": cid, "descricao": "Honorário inicial", "valor": 1000.0}
    # advogado não cria honorário
    assert client.post("/api/v1/financeiro/honorarios", json=payload, headers=adv).status_code == 403
    # financeiro cria
    assert client.post("/api/v1/financeiro/honorarios", json=payload, headers=fin).status_code == 201
    # advogado pode ler relatório
    r = client.get("/api/v1/financeiro/relatorio", headers=adv)
    assert r.status_code == 200 and r.json()["pendente"] == 1000.0


def test_password_reset(client):
    register(client)
    req = client.post(
        "/api/v1/auth/password-reset/request", json={"email": "admin@a.com"}
    )
    token = req.json()["reset_token"]
    r = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "nova_senha": "novasenha123"},
    )
    assert r.status_code == 200
    # senha antiga falha, nova funciona
    assert (
        client.post(
            "/api/v1/auth/login",
            data={"username": "admin@a.com", "password": "senha12345"},
        ).status_code
        == 401
    )
    login(client, "admin@a.com", "novasenha123")


def test_ia_peticao_template(client):
    token = _admin_token(client)
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
    assert r.json()["fonte"] == "template"
    assert "DOS FATOS" in r.json()["texto"]


def test_sem_token_401(client):
    assert client.get("/api/v1/clientes").status_code == 401
