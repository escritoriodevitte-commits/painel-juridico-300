"""
Rotas para Geração de Peças Jurídicas via IA
Integração com OpenAI GPT-4 para geração de documentos jurídicos
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import os

from dependencies import get_current_user, get_current_tenant, get_db
from database import User, Tenant
from services.ia_service import get_ia_service

router = APIRouter(prefix="/ia", tags=["IA - Geração de Peças"])

# ==================== SCHEMAS ====================

class DadosProcesso(BaseModel):
    """Dados do processo jurídico"""
    numero_processo: str = Field(..., description="Número do processo")
    vara: str = Field(..., description="Vara/Tribunal")
    reclamante: str = Field(..., description="Nome do reclamante")
    reclamada: str = Field(..., description="Nome da reclamada")
    valor_pedido: Optional[float] = Field(None, description="Valor da reclamação")
    tese_inicial: Optional[str] = Field(None, description="Tese inicial do reclamante")
    tese_defesa: Optional[str] = Field(None, description="Tese de defesa")
    status: Optional[str] = Field(None, description="Status do processo")

class DadosJuiz(BaseModel):
    """Perfil do juiz"""
    nome: str = Field(..., description="Nome do juiz")
    tendencia_conciliatoria: Optional[str] = None
    postura_justa_causa: Optional[str] = None
    postura_acidente: Optional[str] = None
    postura_danos_morais: Optional[str] = None
    postura_horas_extras: Optional[str] = None
    postura_rescisao_indireta: Optional[str] = None

class Jurisprudencia(BaseModel):
    """Jurisprudência/Súmula"""
    tipo: str = Field(..., description="Tipo: súmula, jurisprudência, lei")
    titulo: str = Field(..., description="Título da súmula/jurisprudência")
    tema: str = Field(..., description="Tema")
    fonte: Optional[str] = None
    trecho: Optional[str] = None

class GerarPecaRequest(BaseModel):
    """Request para geração de peça jurídica"""
    tipo_peca: str = Field(..., description="Tipo de peça: reclamatoria_trabalhista, contestacao, etc")
    dados_processo: DadosProcesso
    dados_juiz: Optional[DadosJuiz] = None
    jurisprudencia: Optional[List[Jurisprudencia]] = None
    instrucoes_adicionais: Optional[str] = None

class GerarPecaResponse(BaseModel):
    """Response da geração de peça"""
    sucesso: bool
    conteudo: Optional[str] = None
    tipo_peca: str
    tipo_nome: Optional[str] = None
    gerado_por_ia: Optional[bool] = None
    aviso: Optional[str] = None
    erro: Optional[str] = None
    timestamp: str

# ==================== ENDPOINTS ====================

@router.get("/status")
async def status_ia(
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Verificar status da integração com IA"""
    openai_key = os.getenv("OPENAI_API_KEY")
    ia_service = get_ia_service(openai_key)
    status = ia_service.status_ia()
    
    return {
        "ia_status": status,
        "tenant": tenant.name,
        "mensagem": "Configure OPENAI_API_KEY para usar geração via IA. Sem ela, usa templates locais."
    }

@router.get("/tipos-peca")
async def listar_tipos_peca(
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Listar tipos de peça disponíveis"""
    openai_key = os.getenv("OPENAI_API_KEY")
    ia_service = get_ia_service(openai_key)
    tipos = ia_service.listar_tipos_peca()
    
    return {
        "tipos_peca": tipos,
        "total": len(tipos),
        "descricao": "Tipos de peças jurídicas que podem ser geradas"
    }

@router.post("/gerar-peca", response_model=GerarPecaResponse)
async def gerar_peca(
    request: GerarPecaRequest,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Gerar uma peça jurídica usando IA ou template local
    
    Tipos de peça disponíveis:
    - reclamatoria_trabalhista
    - contestacao
    - alegacoes_finais
    - rol_perguntas
    - recurso_ordinario
    - impugnacao
    - manifestacao
    - pedido_habilitacao
    - procuracao
    - replica
    """
    
    # Validar tipo de peça
    openai_key = os.getenv("OPENAI_API_KEY")
    ia_service = get_ia_service(openai_key)
    
    if not ia_service.validar_tipo_peca(request.tipo_peca):
        tipos_validos = list(ia_service.listar_tipos_peca().keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de peça inválido. Tipos válidos: {', '.join(tipos_validos)}"
        )
    
    # Montar dados do juiz
    perfil_juiz = None
    if request.dados_juiz:
        perfil_juiz = {
            'name': request.dados_juiz.nome,
            'vara': request.dados_processo.vara,
            'tendencia_conciliatoria': request.dados_juiz.tendencia_conciliatoria,
            'postura_justa_causa': request.dados_juiz.postura_justa_causa,
            'postura_acidente': request.dados_juiz.postura_acidente,
            'postura_danos_morais': request.dados_juiz.postura_danos_morais,
            'postura_horas_extras': request.dados_juiz.postura_horas_extras,
            'postura_rescisao_indireta': request.dados_juiz.postura_rescisao_indireta,
        }
    
    # Montar jurisprudência
    jurisprudencia = []
    if request.jurisprudencia:
        jurisprudencia = [
            {
                'tipo': j.tipo,
                'titulo': j.titulo,
                'tema': j.tema,
                'fonte': j.fonte or 'N/A',
                'trecho': j.trecho
            }
            for j in request.jurisprudencia
        ]
    
    # Gerar peça
    resultado = ia_service.gerar_peca_juridica(
        tipo_peca=request.tipo_peca,
        processo_numero=request.dados_processo.numero_processo,
        vara=request.dados_processo.vara,
        reclamante=request.dados_processo.reclamante,
        reclamada=request.dados_processo.reclamada,
        valor_pedido=request.dados_processo.valor_pedido,
        tese_inicial=request.dados_processo.tese_inicial,
        tese_defesa=request.dados_processo.tese_defesa,
        status=request.dados_processo.status,
        juiz_nome=request.dados_juiz.nome if request.dados_juiz else None,
        perfil_juiz=perfil_juiz,
        jurisprudencia=jurisprudencia,
        instrucoes_adicionais=request.instrucoes_adicionais,
    )
    
    if not resultado['sucesso']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resultado.get('erro', 'Erro desconhecido ao gerar peça')
        )
    
    return GerarPecaResponse(
        sucesso=resultado['sucesso'],
        conteudo=resultado.get('conteudo'),
        tipo_peca=resultado['tipo_peca'],
        tipo_nome=resultado.get('tipo_nome'),
        gerado_por_ia=resultado.get('gerado_por_ia'),
        aviso=resultado.get('aviso'),
        timestamp=resultado['timestamp']
    )

@router.post("/configurar-openai")
async def configurar_openai_key(
    api_key: str = Body(..., embed=True),
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Configurar a chave da OpenAI API
    
    Apenas administradores podem fazer isso.
    A chave será usada para gerar peças via IA em tempo real.
    """
    from database import UserRole
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem configurar a chave da OpenAI"
        )
    
    if not api_key or len(api_key.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key não pode estar vazia"
        )
    
    # Atualizar a chave (será usada para próximas gerações)
    ia_service = get_ia_service()
    ia_service.atualizar_api_key(api_key)
    
    # Testar a conexão
    status_ia = ia_service.status_ia()
    
    return {
        "mensagem": "Chave da OpenAI configurada com sucesso",
        "ia_disponivel": status_ia['ia_disponivel'],
        "modelo": status_ia['modelo'],
        "aviso": "⚠️ Guarde a chave com segurança. Esta chave tem acesso a sua conta OpenAI."
    }
