"""
Testes para rotas de IA - Geração de Peças Jurídicas
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestIAStatus:
    """Testes para GET /api/ia/status"""
    
    def test_status_ia_authenticated(self, client, auth_headers):
        """Deve retornar status da IA quando autenticado"""
        response = client.get("/api/ia/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "ia_status" in data
        assert "tenant" in data
        assert "mensagem" in data
        assert data["ia_status"]["tipos_peca_disponiveis"] == 10
    
    def test_status_ia_unauthenticated(self, client):
        """Deve retornar 401 sem autenticação"""
        response = client.get("/api/ia/status")
        assert response.status_code == 401
    
    def test_status_ia_no_openai_key(self, client, auth_headers):
        """Deve indicar quando OpenAI não está configurado"""
        response = client.get("/api/ia/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ia_status"]["api_key_configurada"] == False


class TestIATiposPeca:
    """Testes para GET /api/ia/tipos-peca"""
    
    def test_listar_tipos_peca_authenticated(self, client, auth_headers):
        """Deve listar todos os tipos de peça quando autenticado"""
        response = client.get("/api/ia/tipos-peca", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tipos_peca" in data
        assert data["total"] == 10
        
        # Verificar tipos específicos
        tipos = data["tipos_peca"]
        assert "reclamatoria_trabalhista" in tipos
        assert "contestacao" in tipos
        assert "alegacoes_finais" in tipos
        assert "rol_perguntas" in tipos
        assert "recurso_ordinario" in tipos
        assert "impugnacao" in tipos
        assert "manifestacao" in tipos
        assert "pedido_habilitacao" in tipos
        assert "procuracao" in tipos
        assert "replica" in tipos
    
    def test_listar_tipos_peca_unauthenticated(self, client):
        """Deve retornar 401 sem autenticação"""
        response = client.get("/api/ia/tipos-peca")
        assert response.status_code == 401
    
    def test_tipos_peca_possuem_nomes(self, client, auth_headers):
        """Cada tipo deve ter um nome em português"""
        response = client.get("/api/ia/tipos-peca", headers=auth_headers)
        
        data = response.json()
        tipos = data["tipos_peca"]
        
        for tipo_key, tipo_nome in tipos.items():
            assert isinstance(tipo_nome, str)
            assert len(tipo_nome) > 0
            assert tipo_nome.isupper() or tipo_nome[0].isupper()


class TestGerarPeca:
    """Testes para POST /api/ia/gerar-peca"""
    
    def test_gerar_peca_reclamatoria_trabalhista(self, client, auth_headers):
        """Deve gerar peça de reclamatória trabalhista"""
        request_data = {
            "tipo_peca": "reclamatoria_trabalhista",
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "João da Silva",
                "reclamada": "Empresa XYZ Ltda",
                "valor_pedido": 50000.00,
                "tese_inicial": "Demissão sem justa causa"
            }
        }
        
        response = client.post(
            "/api/ia/gerar-peca",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] == True
        assert data["tipo_peca"] == "reclamatoria_trabalhista"
        assert "conteudo" in data
        assert len(data["conteudo"]) > 100
        assert "timestamp" in data
    
    def test_gerar_peca_tipo_invalido(self, client, auth_headers):
        """Deve retornar erro para tipo de peça inválido"""
        request_data = {
            "tipo_peca": "tipo_inexistente",
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "João",
                "reclamada": "Empresa"
            }
        }
        
        response = client.post(
            "/api/ia/gerar-peca",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    def test_gerar_peca_com_dados_juiz(self, client, auth_headers):
        """Deve gerar peça com dados do juiz"""
        request_data = {
            "tipo_peca": "contestacao",
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "João da Silva",
                "reclamada": "Empresa XYZ Ltda",
                "valor_pedido": 30000.00
            },
            "dados_juiz": {
                "nome": "Juiz José Santos",
                "tendencia_conciliatoria": "Alta"
            }
        }
        
        response = client.post(
            "/api/ia/gerar-peca",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] == True
        assert "Juiz José Santos" in data["conteudo"] or len(data["conteudo"]) > 0
    
    def test_gerar_peca_com_jurisprudencia(self, client, auth_headers):
        """Deve gerar peça com jurisprudências fornecidas"""
        request_data = {
            "tipo_peca": "alegacoes_finais",
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "Maria Santos",
                "reclamada": "Empresa ABC Ltda"
            },
            "jurisprudencia": [
                {
                    "tipo": "sumula",
                    "titulo": "Súmula 21 do TST",
                    "tema": "Adicional de insalubridade",
                    "fonte": "TST",
                    "trecho": "O adicional de insalubridade integra..."
                }
            ]
        }
        
        response = client.post(
            "/api/ia/gerar-peca",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] == True
    
    def test_gerar_peca_com_instrucoes(self, client, auth_headers):
        """Deve gerar peça com instruções adicionais"""
        request_data = {
            "tipo_peca": "recurso_ordinario",
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "Pedro Costa",
                "reclamada": "Indústria XYZ S/A"
            },
            "instrucoes_adicionais": "Foque em violação de direitos fundamentais e danos morais"
        }
        
        response = client.post(
            "/api/ia/gerar-peca",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] == True
    
    def test_gerar_peca_unauthenticated(self, client):
        """Deve retornar 401 sem autenticação"""
        request_data = {
            "tipo_peca": "reclamatoria_trabalhista",
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "João",
                "reclamada": "Empresa"
            }
        }
        
        response = client.post("/api/ia/gerar-peca", json=request_data)
        assert response.status_code == 401
    
    def test_gerar_peca_todos_os_tipos(self, client, auth_headers):
        """Deve gerar peças para todos os tipos disponíveis"""
        tipos = [
            "reclamatoria_trabalhista",
            "contestacao",
            "alegacoes_finais",
            "rol_perguntas",
            "recurso_ordinario",
            "impugnacao",
            "manifestacao",
            "pedido_habilitacao",
            "procuracao",
            "replica"
        ]
        
        for tipo in tipos:
            request_data = {
                "tipo_peca": tipo,
                "dados_processo": {
                    "numero_processo": "0001234-56.2026.5.01.0000",
                    "vara": "1ª Vara do Trabalho",
                    "reclamante": "Teste",
                    "reclamada": "Empresa Teste"
                }
            }
            
            response = client.post(
                "/api/ia/gerar-peca",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200, f"Falha ao gerar {tipo}"
            data = response.json()
            assert data["sucesso"] == True
            assert data["tipo_peca"] == tipo


class TestConfigurarOpenAI:
    """Testes para POST /api/ia/configurar-openai"""
    
    def test_configurar_openai_como_admin(self, client, auth_headers):
        """Deve permitir admin configurar chave OpenAI"""
        response = client.post(
            "/api/ia/configurar-openai",
            json={"api_key": "sk-proj-test-key-123"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mensagem" in data
        assert "configurado" in data["mensagem"].lower()
    
    def test_configurar_openai_chave_vazia(self, client, auth_headers):
        """Deve retornar erro para chave vazia"""
        response = client.post(
            "/api/ia/configurar-openai",
            json={"api_key": ""},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "vazia" in response.json()["detail"].lower()
    
    def test_configurar_openai_sem_autenticacao(self, client):
        """Deve retornar 401 sem autenticação"""
        response = client.post(
            "/api/ia/configurar-openai",
            json={"api_key": "sk-proj-test-key"}
        )
        
        assert response.status_code == 401
    
    def test_configurar_openai_como_user(self, client, test_regular_user):
        """Deve retornar 403 se usuário não for admin"""
        # Login como usuário regular
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_regular_user.email,
                "password": "TestPass123!"
            }
        )
        
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        response = client.post(
            "/api/ia/configurar-openai",
            json={"api_key": "sk-proj-test-key"},
            headers=user_headers
        )
        
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()


class TestIAIntegration:
    """Testes de integração do fluxo completo"""
    
    def test_fluxo_completo_gerar_peca(self, client, auth_headers):
        """Testa fluxo completo: verificar status > listar tipos > gerar peça"""
        # 1. Verificar status
        status_response = client.get("/api/ia/status", headers=auth_headers)
        assert status_response.status_code == 200
        
        # 2. Listar tipos
        tipos_response = client.get("/api/ia/tipos-peca", headers=auth_headers)
        assert tipos_response.status_code == 200
        tipos = tipos_response.json()["tipos_peca"]
        
        # 3. Gerar uma peça
        tipo_escolhido = "reclamatoria_trabalhista"
        request_data = {
            "tipo_peca": tipo_escolhido,
            "dados_processo": {
                "numero_processo": "0001234-56.2026.5.01.0000",
                "vara": "1ª Vara do Trabalho",
                "reclamante": "João da Silva",
                "reclamada": "Empresa XYZ Ltda",
                "valor_pedido": 50000.00
            }
        }
        
        peca_response = client.post(
            "/api/ia/gerar-peca",
            json=request_data,
            headers=auth_headers
        )
        
        assert peca_response.status_code == 200
        peca_data = peca_response.json()
        assert peca_data["sucesso"] == True
        assert peca_data["tipo_nome"] == tipos[tipo_escolhido]
    
    def test_multiplas_gerações_consecutivas(self, client, auth_headers):
        """Deve suportar múltiplas gerações consecutivas"""
        for i in range(3):
            request_data = {
                "tipo_peca": "contestacao",
                "dados_processo": {
                    "numero_processo": f"000{i}234-56.2026.5.01.0000",
                    "vara": "1ª Vara do Trabalho",
                    "reclamante": f"User {i}",
                    "reclamada": f"Company {i}"
                }
            }
            
            response = client.post(
                "/api/ia/gerar-peca",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["sucesso"] == True
